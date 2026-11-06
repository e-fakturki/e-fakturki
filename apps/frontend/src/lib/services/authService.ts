import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { apiConfig } from "../../config";
import { useCurrentUserStore } from "../../stores/currentUserStore";
import type { LoginRequest, SignUpRequest, LoginResponse } from "../types/auth";
import router from "../../router/router";

const baseUrl = apiConfig.apiBaseUrl + apiConfig.endpoints.auth;

// Axios interceptor to add the JWT token to all requests
axios.interceptors.request.use((config) => {
  const currentUserStore = useCurrentUserStore();
  const token = currentUserStore.getToken;

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Axios interceptor to handle 401 responses
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      userLogout();
      router.push("/login");
    }

    return Promise.reject(error);
  },
);

// let isRefreshing = false;
// let failedQueue: any[] = [];

// const processQueue = (error: any, token: string | null = null) => {
//   failedQueue.forEach((prom) => {
//     if (error) {
//       prom.reject(error);
//     } else {
//       prom.resolve(token);
//     }
//   });
//   failedQueue = [];
// };

// axios.interceptors.response.use(
//   (response) => response,
//   async (error) => {
//     const originalRequest = error.config;
//     const currentUserStore = useCurrentUserStore();

//     if (error.response?.status === 401 && !originalRequest._retry) {
//       if (isRefreshing) {
//         // 🔥 kolejkuj requesty
//         return new Promise((resolve, reject) => {
//           failedQueue.push({ resolve, reject });
//         }).then((token) => {
//           originalRequest.headers.Authorization = `Bearer ${token}`;
//           return axios(originalRequest);
//         });
//       }

//       originalRequest._retry = true;
//       isRefreshing = true;

//       try {
//         const response = await axios.post(baseUrl + "/auth/refresh", {}, { withCredentials: true });

//         const newToken = response.data.access_token;

//         currentUserStore.setToken(newToken);

//         processQueue(null, newToken);

//         originalRequest.headers.Authorization = `Bearer ${newToken}`;
//         return axios(originalRequest);
//       } catch (err) {
//         processQueue(err, null);
//         userLogout();
//         router.push("/login");
//         return Promise.reject(err);
//       } finally {
//         isRefreshing = false;
//       }
//     }

//     return Promise.reject(error);
//   },
// );

export const decodeToken = (token: string): any => {
  try {
    return jwtDecode(token);
  } catch (error) {
    console.error("Invalid token:", error);
    return null;
  }
};

export const userLogin = async (data: LoginRequest): Promise<LoginResponse> => {
  try {
    const formData = new URLSearchParams();
    formData.append("grant_type", data.grant_type ?? "");
    formData.append("username", data.username);
    formData.append("password", data.password);
    formData.append("scope", data.scope ?? "");
    formData.append("client_id", data.client_id ?? "");
    formData.append("client_secret", data.client_secret ?? "");

    const response = await axios.post<LoginResponse>(baseUrl + "/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      withCredentials: true,
    });
    return response.data;
  } catch (error: any) {
    throw error.response.status;
  }
};

export const userLogout = () => {
  const currentUserStore = useCurrentUserStore();
  currentUserStore.setToken("");
  currentUserStore.setUserData(null as any, null as any, null as any, null as any, null as any);
  currentUserStore.setCompanyData(null as any);
};

export const userSignUp = async (data: SignUpRequest): Promise<LoginResponse> => {
  try {
    const response = await axios.post<LoginResponse>(baseUrl + "/signup", data);
    return response.data;
  } catch (error: any) {
    throw error.response.status;
  }
};
