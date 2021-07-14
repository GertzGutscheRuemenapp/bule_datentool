import gql from 'graphql-tag'
import { User } from './users';

export const ALL_USERS_QUERY = gql`
    query {
      allUsers{
        id, userName, email, firstName, lastName,
        canEditData, canCreateScenarios, adminAccess, isSuperuser
      }
    }
`;

export const CREATE_USER_QUERY = gql`
    mutation createUser($userName: String!, $password: String!){
      createUser(userName: $userName, password: $password){
        user { id, userName }, ok
      }
     }
`;

export const DELETE_USER_QUERY = gql`
    mutation deleteUser($id: ID!){
      deleteUser(id: $id){
        ok
      }
     }
`;

export const UPDATE_ACCOUNT_QUERY = gql`
    mutation updateUser($id: ID!, $userName: String!, $email: String, $firstName: String, $lastName: String,
        $password: String){
      updateUser(id: $id, userName: $userName, email: $email, firstName: $firstName, lastName: $lastName,
        password: $password){
        user{
          id, userName
        }
      }
    }
`;

export const UPDATE_PERMISSIONS_QUERY = gql`
    mutation updateUser($id: ID!,$canEditData: Boolean, $canCreateScenarios: Boolean, $adminAccess: Boolean){
      updateUser(id: $id, canEditData: $canEditData, canCreateScenarios: $canCreateScenarios, adminAccess: $adminAccess){
        user{
          id, userName
        }
      }
    }
`;

export type GetUsersQuery = {
  allUsers: User[];
}

