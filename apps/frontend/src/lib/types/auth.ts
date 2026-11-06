export interface LoginRequest {
  grant_type: string | null;
  username: string;
  password: string;
  scope: string | null;
  client_id: string | null;
  client_secret: string | null;
}

export interface SignUpRequest {
  name: string;
  last_name: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}
