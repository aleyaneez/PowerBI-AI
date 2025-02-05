import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "../pages/Home";
import Reports from "../pages/Reports";
import MainLayout from "../layouts/MainLayout";

const AppRouter = () => {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </MainLayout>
    </Router>
  );
};

export default AppRouter;