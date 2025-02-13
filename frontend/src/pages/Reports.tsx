import React, { useContext, useState, useEffect } from "react";
import { PDFContext } from "../context/PDFContext";
import { parseFilename } from "../utils/parseFilename";
import ExportButton from "../components/ExportButton";
import PageCard from "../components/PageCard";
import { getCompanyDisplayName } from "../utils/companyDictionary";
import { capitalize } from "../utils/capitalize";
import LoadingContainer from "../components/LoadingContainer";

let hasFetched = false;

const Reports: React.FC = () => {
  const {
    pdfFile,
    observations,
    setObservations,
    setExcludes,
    setPngUrls,
    company,
    setCompany,
    week,
    setWeek,
    setPdfName,
  } = useContext(PDFContext);

  const [companyName, setCompanyName] = useState<string>("");
  const [displayWeek, setDisplayWeek] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!pdfFile || observations.length > 0 || hasFetched) return;

    const fetchObservations = async () => {
      const startTime = performance.now();

      try {
        const filename = pdfFile.split("/").pop() || "";
        const parsed = parseFilename(filename);

        setCompany(parsed.company);
        setWeek(parsed.week);
        setPdfName(parsed.company);

        setCompanyName(getCompanyDisplayName(parsed.company));
        setDisplayWeek(parsed.week);

        const formData = new FormData();
        formData.append("company", parsed.company);
        formData.append("week", parsed.week);
        formData.append("pdfName", parsed.company);

        setIsLoading(true);
        const response = await fetch("http://localhost:8000/generate-observations", {
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
        setPngUrls(data.png_urls);
        
        const endTime = performance.now();
        console.log(`Tiempo de respuesta: ${(endTime - startTime).toFixed(2)} ms`);
        
        setIsLoading(false);
        hasFetched = true;

      } catch (error) {
        console.error("Error al obtener observaciones:", error);
        setIsLoading(false);
      }
    };

    fetchObservations();
  }, [
    pdfFile,
    observations.length,
    setObservations,
    setExcludes,
    setPngUrls,
    setCompany,
    setWeek,
    setPdfName
  ]);

  if (!pdfFile) {
    return <p className="text-primary">No se ha subido ningún PDF.</p>;
  }

  return (
    <div className="max-w-7xl mx-auto justify-center items-center flex flex-col">
      {isLoading ? (
        <LoadingContainer
          color="#283575"
          size={16}
        />
      ) : (
        <>
          <h1 className="text-xl font-bold text-primary">
            Reporte de {capitalize(companyName)} semana {displayWeek}
          </h1>
          {/* Renderizar las tarjetas con imágenes PNG y observaciones */}
          <PageCard />

          {/* Botón para exportar el PDF final; al hacer clic se abre en una nueva pestaña */}
          <div className="flex justify-center">
            <ExportButton company={company} week={week} />
          </div>
        </>
      )}
    </div>
  );
};

export default Reports;