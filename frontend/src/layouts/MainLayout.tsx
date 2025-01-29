import { ReactNode } from "react";
import Navbar from "../components/Navbar";

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout = ({ children }: MainLayoutProps) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow p-4">{children}</main>
      <footer className="bg-transparent text-white p-4 text-center">Footer</footer>
    </div>
  );
};

export default MainLayout;