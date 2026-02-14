import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import ClientDashboard from "./pages/ClientDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import Unauthorized from "./pages/Unauthorized";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import Signup from "./pages/SignUp";
import Navbar2 from "./components/Navbar2";
import Landing2 from "./components/Landing2";
import About from "./components/About";
import FAQ from "./components/FAQ";
import Contact from "./components/Contact";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <>
              <Navbar2 />
              <Landing2 />
            </>
          }
        />
        <Route
          path="/about"
          element={
            <>
              <Navbar2 />
              <About />
            </>
          }
        />
        <Route
          path="/faq"
          element={
            <>
              <Navbar2 />
              <FAQ />
            </>
          }
        />
        <Route
          path="/contact"
          element={
            <>
              <Navbar2 />
              <Contact />
            </>
          }
        />
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/client"
          element={
            <ProtectedRoute role="client">
              <Navbar />
              <ClientDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin"
          element={
            <ProtectedRoute role="admin">
              <Navbar />
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route path="/unauthorized" element={<Unauthorized />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
