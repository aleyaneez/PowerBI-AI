import React from "react";
import Button from '../components/Button';
import Examples from '../components/Examples';
import { FileUp } from 'lucide-react';

const Home: React.FC = () => {
  const examples = [
    "abastible_consolidado_2025-01-20.pdf",
    "albemarle_2025-01-20.pdf",
    "enex_2025-01-20.pdf"
  ];

  return (
    <div className="flex flex-col justify-center items-center">
      <h1 className="text-3xl font-bold text-primary">¡Bienvenido!</h1>
      <div className="mt-5 flex flex-col items-center text-center">
        <p className="text-primary font-medium text-lg">
          Genera las observaciones de reportes semanales de RAEV/100 con inteligencia artificial, deberás subir el reporte en formato pdf que en su nombre <br /> indique el cliente a reportar seguido de la semana objetivo. ¡Puedes guiarte con los ejemplos a continuación!
        </p>
        <Examples examples={examples} interval={5000} />
        <Button text="Subir PDF" icon={<FileUp size={20} />} className="mt-5" />
      </div>
    </div>
  );
};

export default Home;