import React from 'react';
import { Page } from 'react-pdf';

interface ObservationCardProps {
  pageNumber: number;
  observation: string;
  excluded?: boolean;
}

const ObservationCard: React.FC<ObservationCardProps> = ({
  pageNumber,
  observation,
  excluded = false,
}) => {
  return (
    <div className="min-w-[300px] border p-4 m-2 rounded shadow">
      <h3 className="font-bold mb-2">Página {pageNumber}</h3>
      <div className="border mb-2">
        <Page pageNumber={pageNumber} width={280} />
      </div>
      {!excluded && (
        <div className="p-2 border rounded bg-gray-100">
          <p className="text-sm">{observation || "Sin observación"}</p>
        </div>
      )}
    </div>
  );
};

export default ObservationCard;