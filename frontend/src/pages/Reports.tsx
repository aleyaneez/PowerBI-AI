import React, { useContext, useState, useEffect } from "react";
import { Document, Page } from "react-pdf";
import { PDFContext } from "../context/PDFContext";
import { parseFilename } from "../utils/parseFilename";
import ExportButton from "../components/ExportButton";
import PageCard from "../components/PageCard";

let hasFetched = false;

const Reports: React.FC = () => {
  const { pdfFile, observations, setObservations, setExcludes } = useContext(PDFContext);
  const [numPages, setNumPages] = useState<number>(0);
  const [finalPdfUrl, setFinalPdfUrl] = useState<string>("");

  useEffect(() => {
    if (!pdfFile || observations.length > 0 || hasFetched) return;
    
    const fetchObservations = async () => {
      let company = "";
      let week = "";
      let pdfName = "";
      try {
        const filename = pdfFile.split("/").pop() || "";
        const parsed = parseFilename(filename);
        company = parsed.company;
        week = parsed.week;
        pdfName = company;
      } catch (error) {
        console.error("Error al extraer company y week:", error);
        return;
      }
      
      const formData = new FormData();
      formData.append("company", company);
      formData.append("week", week);
      formData.append("pdfName", pdfName);
      try {
        const response = await fetch("http://localhost:8000/finalize", {
          method: "POST",
          body: formData,
        });
        if (!response.ok) {
          throw new Error("Error en la generación de observaciones");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        setObservations(data.observations);
        setExcludes(data.excludes);
        setFinalPdfUrl(data.final_pdf_url);
        hasFetched = true;
      } catch (error) {
        console.error("Error al obtener observaciones:", error);
      }
    };

    fetchObservations();
  }, [pdfFile, observations.length, setObservations, setExcludes]);

  if (!pdfFile) {
    return <p className="text-primary">No se ha subido ningún PDF.</p>;
  }

  const fileName = pdfFile.split("/").pop() || "Reporte.pdf";

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

      {/* Vista preliminar del PDF */}
      <div className="bg-white shadow rounded p-4 mb-6">
        <Document
          file={finalPdfUrl ? finalPdfUrl : pdfFile}
          onLoadSuccess={({ numPages }) => setNumPages(numPages)}
          onLoadError={(error) => console.error("Error al cargar el PDF:", error)}
        >
          {numPages >= 2 ? (
            <Page pageNumber={2} className="border" />
          ) : (
            <Page pageNumber={1} className="border" />
          )}
        </Document>
      </div>

      {/* Renderizar las tarjetas con observaciones con desplazamiento horizontal */}
      <PageCard />

      {/* Botón para exportar el PDF final; al hacer clic se abre en una nueva pestaña */}
      <div className="flex justify-center">
        <ExportButton finalPdfUrl={finalPdfUrl} />
      </div>
    </div>
  );
};

export default Reports;