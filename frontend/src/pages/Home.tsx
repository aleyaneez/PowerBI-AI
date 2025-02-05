import React, { useContext } from "react";
import Examples from '../components/Examples';
import DragDrop from "../components/DragDrop";
import { PDFContext } from "../context/PDFContext";

const Home: React.FC = () => {
  const examples = [
    "abastible_consolidado_2025-01-20.pdf",
    "albemarle_2025-01-20.pdf",
    "enex_2025-01-13.pdf",
    "centinela_2025-01-27.pdf",
  ];

  const { setPdfFile } = useContext(PDFContext);

  const handleFileAccepted = (file: File) => {
    setPdfFile(file);
  };

  return (
    <div className="flex flex-col justify-center items-center">
      <h1 className="text-3xl font-bold text-primary">¡Bienvenido/a!</h1>
      <div className="mt-5 flex flex-col items-center text-center">
        <p className="text-primary font-medium text-lg">
          Genera las observaciones de reportes semanales de RAEV/100 con inteligencia artificial, deberás subir el reporte en formato pdf que en su nombre <br /> indique el cliente a reportar seguido de la semana objetivo. ¡Puedes guiarte con los ejemplos a continuación!
        </p>
        <Examples examples={examples} interval={5000} />
        <div className="mt-5 w-full max-w-md">
          <DragDrop onFileAccepted={handleFileAccepted} />
        </div>
      </div>
    </div>
  );
};

export default Home;