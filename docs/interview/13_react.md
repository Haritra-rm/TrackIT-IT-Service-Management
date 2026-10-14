# 13. React 18, Vite & Modern Frontend State Management

### 1. What it is
React is a declarative, component-based JavaScript library for building interactive user interfaces. Vite is a next-generation frontend build tool powered by native ES modules and Rollup.

### 2. Why TrackIT uses it
An IT service management platform requires interactive dashboards, live SLA countdown timers, dynamic ticket queue filtering, modal dialogs, and instant status updates without full-page reloads.

### 3. How it works
- **Authentication Context (`AuthContext`)**: Stores authenticated user session, JWT token, and derived boolean flags (`isAdmin`, `isAgent`, `isEmployee`). Wrapped at the top level of the component tree to provide global auth state via `useAuth()`.
- **Protected Routing (`ProtectedRoute`)**: Wraps React Router v6 routes. If a user is unauthenticated, they are redirected to `/login`. If an authenticated employee navigates directly to `/users` or `/categories`, they are redirected to `/` with no privilege escalation.
- **API Interceptor with Centralized Error Handling**: In `api.js`, all outbound HTTP requests automatically append `Authorization: Bearer <token>`. If the backend returns a 401 Unauthorized, the client purges expired local storage tokens and dispatches an event to redirect to `/login`.
- **Reusable Component Architecture**: UI components (`StatusBadge`, `PriorityBadge`, `SlaBadge`, `StatCard`, `TicketTable`, `Modal`, `ConfirmDialog`) ensure visual consistency across all pages.

### 4. Where it exists in the code
- Router & Route Guards: [`frontend/src/App.jsx`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/App.jsx)
- Auth Context: [`frontend/src/context/AuthContext.jsx`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/context/AuthContext.jsx)
- API Interceptor: [`frontend/src/services/api.js`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/services/api.js)
- Component Library: [`frontend/src/components/`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/components/)

### 5. Alternative approach
- Server-side rendered templates using Django / Jinja2 / Thymeleaf.
- Vanilla JavaScript with raw DOM manipulation.
- Angular or Vue.js.

### 6. Why this approach was selected
Server-side HTML rendering (Jinja2) forces a full browser reload on every status update, comment post, or filter change, degrading user experience. React's virtual DOM reconciliation updates only the specific table row or badge that changed. Compared to Angular, React has a lighter footprint and faster iteration cycle, and Vite provides sub-second Hot Module Replacement (HMR).

### 7. Likely interviewer question
*"How do you handle user authentication state and prevent unauthorized access to Admin pages in React?"*

### 8. Simple fresher-level answer
*"I use a React `AuthProvider` with React Context to manage authentication state globally. In `App.jsx`, sensitive routes like `/users` and `/categories` are wrapped in a `<ProtectedRoute allowedRoles={['ADMIN']}>` component. If a user is not logged in or lacks the Admin role, the guard redirects them back to the dashboard. Furthermore, we never rely on the frontend alone: every backend API endpoint independently verifies the user's role and returns a 403 Forbidden if bypassed."*
