import { Link } from "react-router-dom";
import LogoMigtra from "../assets/migtra.png";

const Navbar = () => {
  return (
    <nav className="p-4 text-white bg-transparent">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/">
          <img src={LogoMigtra} alt="Migtra" className="w-48" />
        </Link>
        <ul className="flex space-x-4 list-none">
          <li>
            <Link to="/" className="text-primary">Inicio</Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;