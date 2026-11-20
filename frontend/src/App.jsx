import { useState } from "react";
import Login from "./pages/Login.jsx";
import Home from "./pages/Home.jsx";

const KEY = "session";

export default function App() {
  const [session, setSession] = useState(() => {
    try {
      return JSON.parse(sessionStorage.getItem(KEY));
    } catch {
      return null;
    }
  });

  const login = (s) => {
    sessionStorage.setItem(KEY, JSON.stringify(s));
    setSession(s);
  };
  const logout = () => {
    sessionStorage.removeItem(KEY);
    setSession(null);
  };

  return session ? <Home session={session} onLogout={logout} /> : <Login onLogin={login} />;
}
