import React from 'react';
import { Page } from 'react-pdf';

interface ObservationCardProps {
  pageNumber: number;
  pdfFile: string; // URL del PDF para renderizar la página
  observation: string;
  excluded?: boolean; // Prop para indicar si la página está excluida
}

const ObservationCard: React.FC<ObservationCardProps> = ({
  pageNumber,
  pdfFile,
  observation,
  excluded = false,
}) => {
  return (
    <div className="min-w-[300px] border p-4 m-2 rounded shadow">
      <h3 className="font-bold mb-2">Página {pageNumber}</h3>
      <div className="border mb-2">
        {/* Renderizamos la página usando react-pdf */}
        <Page pageNumber={pageNumber} file={pdfFile} width={280} />
      </div>
      {/* Solo se muestra el recuadro de observación si la página no está excluida */}
      {!excluded && (
        <div className="p-2 border rounded bg-gray-100">
          <p className="text-sm">{observation || "Sin observación"}</p>
        </div>
      )}
    </div>
  );
};

export default ObservationCard;