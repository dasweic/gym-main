
const API_BASE_URL = "http://127.0.0.1:8000";

const Auth = {
    getToken() {
        return sessionStorage.getItem("access_token");
    },

    saveToken(token) {
        sessionStorage.setItem("access_token", token);
    },

    clear() {
        sessionStorage.removeItem("access_token");
    },

    isLoggedIn() {
        return Boolean(this.getToken());
    },
};

async function apiRequest(path, options = {}) {
    const headers = {
        ...options.headers,
        "Content-Type": "application/json",
    };

    const token = Auth.getToken();

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    let response;

    try {
        response = await fetch(`${API_BASE_URL}${path}`, {
            ...options,
            headers,
        });
    } catch (error) {
        throw new Error(
            "Backend se connection nahi ho raha. Check karo FastAPI server running hai ya nahi."
        );
    }

    if (response.status === 401) {
        Auth.clear();
        throw new Error("Invalid phone/email or password.");
    }

    if (response.status === 403) {
        let message = "Access denied.";

        try {
            const error = await response.json();
            message = error.detail || message;
        } catch {}

        throw new Error(message);
    }

    if (!response.ok) {
        let message = `Request failed (${response.status})`;

        try {
            const error = await response.json();
            message =
                typeof error.detail === "string"
                    ? error.detail
                    : message;
        } catch {}

        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

const GymAPI = {
    // Phone number OR email login
    async login(identifier, password) {
        const value = identifier.trim();

        if (!value || !password) {
            throw new Error("Phone number/email aur password enter karo.");
        }

        const payload = value.includes("@")
            ? {
                  email: value.toLowerCase(),
                  password,
              }
            : {
                  phone: value,
                  password,
              };

        const result = await apiRequest("/auth/login", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        if (!result.access_token) {
            throw new Error("Login response mein access token nahi mila.");
        }

        Auth.saveToken(result.access_token);

        return result;
    },

    async me() {
        return apiRequest("/auth/me");
    },

    async getProfile() {
        return apiRequest("/member-portal/profile");
    },

    async updateProfile(data) {
        return apiRequest("/member-portal/profile", {
            method: "PUT",
            body: JSON.stringify(data),
        });
    },

    async getSubscription() {
        return apiRequest("/member-portal/subscription");
    },

    async getAttendance() {
        return apiRequest("/member-portal/attendance");
    },

    async getWorkouts() {
        return apiRequest("/member-portal/workouts");
    },

    logout() {
        Auth.clear();
        window.location.href = "../public/login.html";
    },
};

window.GymAPI = GymAPI;
window.GymAuth = Auth;
