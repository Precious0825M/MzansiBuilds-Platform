const API_BASE_URL = 'http://localhost:8000/api';

// Core Request Handler -- for internal use only
async function request(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('token');

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {

        headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
        },
        ...options,
    });

    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.detail || 'API request failed');
    }
    return data;
}

// Authentication APIs
export const api = {
    // LOGIN
    login: ({ email, password }: { email: string; password: string }) =>
        request("/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password }),
        }),

    // REGISTER
    register: ({ name, email, password, bio }: { name: string; email: string; password: string; bio?: string }) =>
        request("/auth/register", {
            method: "POST",
            body: JSON.stringify({
                name,
                email,
                password,
                bio: bio || "",
            }),
        }),

    // Get current user
    getMe: () => request("/users/me"),

    // Get any user by ID
    getUser: (userId: number) => request(`/users/${userId}`),

    // Update user profile
    updateUser: (userId: number, data: { name?: string; bio?: string }) =>
        request(`/users/${userId}`, {
            method: "PUT",
            body: JSON.stringify(data),
        }),

    // Projects

    getProjects: () => request("/projects"),

    getProject: (id: number) => request(`/projects/${id}`),

    createProject: (data: {
        title: string;
        description: string;
        stage: string;
        support_needed?: string | null;
    }) =>
        request("/projects", {
            method: "POST",
            body: JSON.stringify(data),
        }),

    updateProject: (id: number, data: any) =>
        request(`/projects/${id}`, {
            method: "PUT",
            body: JSON.stringify(data),
        }),

    deleteProject: (id: number) =>
        request(`/projects/${id}`, {
            method: "DELETE",
        }),

    // Get projects by specific user
    getProjectsByUser: (userId: number) =>
        request(`/projects/user/${userId}`),

    // Updates 
    getUpdates: () => request("/updates"),

    getProjectUpdates: (projectId: number) =>
        request(`/projects/${projectId}/updates`),

    createUpdate: (data: { project_id: number; content: string }) =>
        request("/updates", {
            method: "POST",
            body: JSON.stringify(data),
        }),

    deleteUpdate: (updateId: number) =>
        request(`/updates/${updateId}`, {
            method: "DELETE",
        }),

    // Comments
    getComments: (updateId: number) =>
        request(`/updates/${updateId}/comments`),

    createComment: (data: { update_id: number; content: string }) =>
        request("/comments", {
            method: "POST",
            body: JSON.stringify(data),
        }),

    deleteComment: (commentId: number) =>
        request(`/comments/${commentId}`, {
            method: "DELETE",
        }),

    // Collab
    requestCollab: (data: { project_id: number; message: string }) =>
        request("/collaborations", {
            method: "POST",
            body: JSON.stringify(data),
        }),

    getMyCollabs: () => request("/collaborations/me"),

    getProjectCollaborations: (projectId: number) =>
        request(`/projects/${projectId}/collaborations`),

    updateCollaborationStatus: (collabId: number, status: string) =>
        request(`/collaborations/${collabId}`, {
            method: "PATCH",
            body: JSON.stringify({ status }),
        }),

    // celebration Wall
    getCelebrations: () => request("/celebrations"),
};