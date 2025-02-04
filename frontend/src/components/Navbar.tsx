import { Link } from "react-router-dom";
import LogoMigtra from "../assets/Capa-2.png";

const Navbar = () => {
  return (
    <nav className="p-8">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/">
          <img src={LogoMigtra} alt="Migtra" />
        </Link>
        <ul className="flex text-secondary font-medium space-x-8">
          <li>
            <Link to="/">Generar PDF</Link>
          </li>
          <li>
            <Link to="/">Configuración</Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;