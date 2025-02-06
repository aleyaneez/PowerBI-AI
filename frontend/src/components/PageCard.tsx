import React, { useContext } from 'react';
import { PDFContext } from '../context/PDFContext';
import ObservationCard from './ObservationCard';

interface PageCardProps {
  excludes: number[];
}

const PageCard: React.FC<PageCardProps> = ({ excludes }) => {
  const { pdfFile, observations } = useContext(PDFContext);

  if (!pdfFile) return null;

  return (
    <div className="flex overflow-x-auto space-x-4 p-4">
      {observations.map((obs) => {
        const isExcluded = excludes.includes(obs.pageNumber);
        return (
          <ObservationCard
            key={obs.pageNumber}
            pageNumber={obs.pageNumber}
            pdfFile={pdfFile}
            observation={obs.observation}
            excluded={isExcluded}
          />
        );
      })}
    </div>
  );
};

export default PageCard;