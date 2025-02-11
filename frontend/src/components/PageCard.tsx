import React, { useEffect, useState, useContext } from 'react';
import { PDFContext } from '../context/PDFContext';
import { pdfjs, Page } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.js',
  import.meta.url
).toString();

const PageCard: React.FC = () => {
  const { pdfFile, observations, excludes } = useContext(PDFContext);
  console.log("pdfFile:", pdfFile);
  const [pdfDoc, setPdfDoc] = useState<any>(null);

  useEffect(() => {
    if (pdfFile) {
      pdfjs.getDocument({ url: pdfFile, withCredentials: false}).promise
        .then((loadedPdf: any) => {
          console.log("PDF cargado:", loadedPdf);
          setPdfDoc(loadedPdf);
        })
        .catch((error: any) => {
          console.error("Error al cargar el PDF:", error);
        });
    }
  }, [pdfFile]);

  if (!pdfFile || !pdfDoc) return null;

  const totalPages = pdfDoc.numPages;
  console.log("Número de páginas:", totalPages);
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

  return (
    <div className="flex overflow-x-auto space-x-4 p-4">
      {pages.map((pageNumber) => {
        const obs = observations.find(o => o.pageNumber === pageNumber) || {
          pageNumber,
          observation: "",
          approved: false
        };
        const isExcluded = excludes.includes(pageNumber);
        return (
          <div key={pageNumber} className="min-w-[300px] border p-4 m-2 rounded shadow">
            <h3 className="text-center font-bold">Página {pageNumber}</h3>
            <div className="border mb-2">
              <Page pdf={pdfDoc} pageNumber={pageNumber} width={280} />
            </div>
            {!isExcluded && (
              <div className="p-2 border rounded bg-gray-100">
                <p className="text-sm text-center">{obs.observation || "Sin observación"}</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default PageCard;