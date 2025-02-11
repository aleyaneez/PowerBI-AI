import React, { useContext, useState, useEffect } from "react";
import { PDFContext } from "../context/PDFContext";
import { parseFilename } from "../utils/parseFilename";
import ExportButton from "../components/ExportButton";
import PageCard from "../components/PageCard";
import { getCompanyDisplayName } from "../utils/companyDictionary";
import { capitalize } from "../utils/capitalize";
import Loading from "../components/Loading";

let hasFetched = false;

const Reports: React.FC = () => {
  const { pdfFile, observations, setObservations, setExcludes, setPngUrls } = useContext(PDFContext);
  const [finalPdfUrl, setFinalPdfUrl] = useState<string>("");
  const [companyName, setCompanyName] = useState<string>("");
  const [displayWeek, setDisplayWeek] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!pdfFile || observations.length > 0 || hasFetched) return;
    
    const fetchObservations = async () => {
      const startTime = performance.now();
      let company = "";
      let week = "";
      let pdfName = "";
      try {
        const filename = pdfFile.split("/").pop() || "";
        const parsed = parseFilename(filename);
        company = parsed.company;
        const displayName = getCompanyDisplayName(company);
        setCompanyName(displayName);
        week = parsed.week;
        setDisplayWeek(week);
        pdfName = company;
      } catch (error) {
        console.error("Error al extraer company y week:", error);
        return;
      }
      
      const formData = new FormData();
      formData.append("company", company);
      formData.append("week", week);
      formData.append("pdfName", pdfName);
      setIsLoading(true);
      try {
        const response = await fetch("http://localhost:8000/finalize", {
          method: "POST",
          body: formData,
        });
        if (!response.ok) {
          throw new Error("Error en la generación de observaciones");
        }
        const data = await response.json();
        const endTime = performance.now();
        setIsLoading(false);
        console.log("Datos recibidos:", data);
        setObservations(data.observations);
        setExcludes(data.excludes);
        setFinalPdfUrl(data.final_pdf_url);
        setPngUrls(data.png_urls);
        console.log(`Tiempo de respuesta: ${(endTime - startTime).toFixed(2)} ms`);
        hasFetched = true;
      } catch (error) {
        console.error("Error al obtener observaciones:", error);
      }
    };

    fetchObservations();
  }, [pdfFile, observations.length, setObservations, setExcludes, setPngUrls]);

  if (!pdfFile) {
    return <p className="text-primary">No se ha subido ningún PDF.</p>;
  }

  return (
    <div className="max-w-7xl mx-auto justify-center items-center flex flex-col">
      {isLoading ? (
        <Loading />
      ) : (
        <>
          <h1 className="text-xl font-bold text-primary">Reporte de {capitalize(companyName)} semana {displayWeek}</h1>
          {/* Renderizar las tarjetas con imágenes PNG y observaciones */}
          <PageCard />

          {/* Botón para exportar el PDF final; al hacer clic se abre en una nueva pestaña */}
          <div className="flex justify-center">
            <ExportButton finalPdfUrl={finalPdfUrl} />
          </div>
        </>
      )}
    </div>
  );
};

export default Reports;