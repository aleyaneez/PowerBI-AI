import React, { useContext, useState, useEffect } from "react";
import { Document, Page } from "react-pdf";
import { PDFContext, PageObservation } from "../context/PDFContext";
import ExportButton from "../components/ExportButton";

const Reports: React.FC = () => {
  const { pdfFile, observations, setObservations } = useContext(PDFContext);
  const [numPages, setNumPages] = useState<number>(0);

  useEffect(() => {
    if (pdfFile && numPages > 0 && observations.length === 0) {
      const initObs: PageObservation[] = Array.from({ length: numPages }, (_, i) => ({
        pageNumber: i + 1,
        observation: "",
        approved: false,
      }));
      setObservations(initObs);
    }
  }, [pdfFile, numPages, observations, setObservations]);

  if (!pdfFile) {
    return <p className="text-primary">No se ha subido ningún PDF.</p>;
  }

  const fileName = pdfFile ? pdfFile.split("/").pop() || "Reporte.pdf" : "Reporte.pdf";

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Encabezado */}
      <div className="flex flex-col items-center md:items-start md:flex-row md:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-primary">{fileName}</h1>
          {numPages > 0 && (
            <span className="text-gray-600 text-sm">
              Total de páginas: {numPages}
            </span>
          )}
        </div>
      </div>

      {/* Contenedor visual para el PDF en sí (página seleccionada, por ejemplo la 2) */}
      <div className="bg-white shadow rounded p-4 mb-6">
        <Document
          file={pdfFile}
          onLoadSuccess={({ numPages }) => setNumPages(numPages)}
          onLoadError={(error) => console.error("Error al cargar el PDF:", error)}
        >
          {/* Como ejemplo, mostramos la segunda página si existe */}
          {numPages >= 2 ? (
            <Page pageNumber={2} className="border" />
          ) : (
            <Page pageNumber={1} className="border" />
          )}
        </Document>
      </div>

      {/* Observación para la página 2 (o la que quieras manejar) */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-primary mb-2">Observación</h2>
        <textarea
          className="w-full p-3 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-400"
          placeholder="Escribe aquí la observación..."
          value={observations[1]?.observation || ""} 
          onChange={(e) => {
            // Actualizar la observación de la página 2 en el contexto
            setObservations((prev) =>
              prev.map((p) =>
                p.pageNumber === 2
                  ? { ...p, observation: e.target.value }
                  : p
              )
            );
          }}
        />
      </div>

      {/* Botón de exportar PDF final */}
      <div className="flex justify-center">
        <ExportButton />
      </div>
    </div>
  );
};

export default Reports;