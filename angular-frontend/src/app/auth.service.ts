import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Observable, ReplaySubject, Subject, of, BehaviorSubject, throwError } from 'rxjs';
import { User } from './login/users';
import { catchError, filter, switchMap, take, tap } from 'rxjs/operators';
import { RestAPI } from "./rest-api";
import { Router } from "@angular/router";

interface Token {
  access: string;
  refresh: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {

  constructor(private rest: RestAPI, private http: HttpClient ) { }
  // user$ = new BehaviorSubject(null as any);
  user$: Subject<User> = new ReplaySubject<User>()

  login(credentials: { username: string; password: string }): Observable<any> {
      localStorage.removeItem('token');
    let query = this.http.post<Token>(this.rest.URLS.token, credentials)
      .pipe(
        tap(token => {
          this.fetchCurrentUser();
          localStorage.setItem('token', token.access);
          localStorage.setItem('refreshToken', token.refresh);
        })
      );
      return query;
  }

  getCurrentUser(): Observable<User> {
    let user = this.user$.pipe(
      switchMap(user => {
        if (user) {
          return of(user);
        }

        const token = localStorage.getItem('token');
        // if there is token then fetch the current user
        if (token) {
          return this.fetchCurrentUser();
        }

        return of(null);
      })
    );
    return user as Observable<User>;
  }

  fetchCurrentUser(): Observable<User> {
    return this.http.get<User>(this.rest.URLS.currentUser)
      .pipe(
        tap(user => {
          this.user$.next(user);
        })
      );
  }

  refreshToken(): Observable<Token> {
    const refreshToken = localStorage.getItem('refreshToken');
    localStorage.removeItem('token');
    return this.http.post<Token>(
      this.rest.URLS.refreshToken,{ refresh: refreshToken }
    ).pipe(
      tap(token => {
        localStorage.setItem('token', token.access);
        localStorage.setItem('refreshToken', token.refresh);
      })
    );
  }

  logout(): void {
    this.user$.next();
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  }
}

@Injectable()
export class TokenInterceptor implements HttpInterceptor {
  private refreshingInProgress: boolean = false;
  private accessTokenSubject: Subject<string> = new ReplaySubject<string>();

  constructor( private authService: AuthService, private router: Router) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const accessToken = localStorage.getItem('token');

    return next.handle(this.addAuthorizationHeader(req, accessToken || '')).pipe(
      catchError(err => {
        //
        if (err instanceof HttpErrorResponse && err.status === 401) {
          // get refresh tokens
          const refreshToken = localStorage.getItem('refreshToken');
          if (refreshToken && accessToken) {
            return this.refreshToken(req, next);
          }
          return this.logoutAndRedirect(err);
        }
        // refresh token failed
        /*if (err instanceof HttpErrorResponse && err.status === 403) {
          return this.logoutAndRedirect(err);
        }*/
        // other errors
        return throwError(err);
      })
    );
  }

  private addAuthorizationHeader(request: HttpRequest<any>, token: string): HttpRequest<any> {
    if (token) {
      return request.clone({setHeaders: {Authorization: `Bearer ${token}`}});
    }
    return request;
  }

  private logoutAndRedirect(err: any): Observable<HttpEvent<any>> {
    this.authService.logout();
    this.router.navigateByUrl('/login');
    return throwError(err);
  }

  private refreshToken(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.refreshingInProgress) {
      this.refreshingInProgress = true;
      this.accessTokenSubject.next();

      return this.authService.refreshToken().pipe(
        switchMap((res) => {
          this.refreshingInProgress = false;
          this.accessTokenSubject.next(res.access);
          // repeat failed request with new token
          return next.handle(this.addAuthorizationHeader(request, res.access));
        })
      );
    } else {
      // new token
      return this.accessTokenSubject.pipe(
        filter(token => token !== null),
        take(1),
        switchMap(token => {
          // repeat failed request with new token
          return next.handle(this.addAuthorizationHeader(request, token));
        }));
    }
  }
}