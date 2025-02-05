import React from 'react';
import { Page } from 'react-pdf';

export interface PageObservation {
  pageNumber: number;
  observation: string;
  approved: boolean;
}

interface PageCardProps {
  pageData: PageObservation;
  onObservationChange: (pageNumber: number, newObs: string) => void;
  onApprove: (pageNumber: number) => void;
  onClear: (pageNumber: number) => void;
  onRegenerate: (pageNumber: number) => void;
  width?: number;
}

const PageCard: React.FC<PageCardProps> = ({
  pageData,
  onObservationChange,
  onApprove,
  onClear,
  onRegenerate,
  width = 600,
}) => {
  return (
    <div className="border p-4 rounded shadow mb-4">
      {/* Renderizamos la página del PDF */}
      <div className="mb-4">
        <Page pageNumber={pageData.pageNumber} width={width} />
      </div>
      {/* Área de texto para la observación */}
      <textarea
        value={pageData.observation}
        onChange={(e) => onObservationChange(pageData.pageNumber, e.target.value)}
        placeholder="Escribe aquí la observación..."
        className="w-full p-2 border rounded mb-2"
      />
      {/* Botones para manejar la observación */}
      <div className="flex gap-2">
        <button
          onClick={() => onApprove(pageData.pageNumber)}
          className="bg-green-500 text-white px-4 py-2 rounded"
        >
          Aprobado
        </button>
        <button
          onClick={() => onClear(pageData.pageNumber)}
          className="bg-red-500 text-white px-4 py-2 rounded"
        >
          Borrar
        </button>
        <button
          onClick={() => onRegenerate(pageData.pageNumber)}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Regenerar Observación
        </button>
      </div>
    </div>
  );
};

export default PageCard;