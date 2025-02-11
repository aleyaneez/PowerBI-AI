import React from 'react';
import ObservationCard from './ObservationCard';

interface PageContainerProps {
  pageNumber: number;
  pngUrl: string;
  observation: string;
  excluded: boolean;
}

const PageContainer: React.FC<PageContainerProps> = ({ pageNumber, pngUrl, observation, excluded }) => {
  return (
    <div className="min-w-[300px]">
      <h3 className="text-center font-semibold text-tertiary mb-1">Página {pageNumber}</h3>
      <div className="p-2 flex justify-center items-center">
        <img src={pngUrl} alt={`Página ${pageNumber}`} width={900} className="border rounded-sm border-slate-400" />
      </div>
      {!excluded && <ObservationCard observation={observation} />}
    </div>
  );
};

export default PageContainer; 