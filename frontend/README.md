## Frontend (Vue)
The frontend is built using **Vue.js** and interacts with the **Django** backend via API.

### Features
- Course listing and search with filters
- Secure authentication via JWT
- Payment integration
- Real-time chat with WebSocket support
- User dashboards (Creator, Learner, Admin)

### Installation
1. **Navigate to the frontend directory:**
   ```sh
   cd frontend
   ```
2. **Install dependencies:**
   ```sh
   npm install
   ```
3. **Set up environment variables:**
   Create a `.env` file in the root of the frontend directory and add:
   ```sh
   VUE_APP_API_BASE_URL=http://127.0.0.1:8000/api
   ```
4. **Run the development server:**
   ```sh
   npm run serve
   ```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
