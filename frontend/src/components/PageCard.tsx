import React, { useContext } from 'react';
import { PDFContext } from '../context/PDFContext';
import PageContainer from './PageContainer';

const PageCard: React.FC = () => {
  const { pngUrls, observations, excludes } = useContext(PDFContext);

  if (!pngUrls || pngUrls.length === 0) return <p>No se han generado imágenes.</p>;

  return (
    <div className="flex overflow-x-auto snap-x snap-mandatory w-full pb-4"
      style={{ scrollSnapType: "x mandatory" }}
    >
      {pngUrls.map((url, index) => {
        const pageNumber = index + 1;
        const obs = observations.find(o => o.pageNumber === pageNumber) || {
          pageNumber,
          observation: "",
          approved: false
        };
        const isExcluded = excludes.includes(pageNumber - 1);
        return (
          <div
            key={pageNumber}
            className="snap-center flex-shrink-0 w-full"
          >
          <PageContainer
            key={pageNumber}
            pageNumber={pageNumber}
            pngUrl={url}
            observation={obs.observation}
            excluded={isExcluded}
          />
          </div>
        );
      })}
    </div>
  );
};

export default PageCard;  