import React, { useContext, useState } from 'react';
import { PDFContext } from '../context/PDFContext';
import Button from './Button';
import { FileDown } from 'lucide-react';
import { parseFilename } from '../utils/parseFilename';
import Loading from './Loading';

const ExportButton: React.FC = () => {
  const { pdfFile, setObservations, setExcludes } = useContext(PDFContext);
  const [loading, setLoading] = useState(false);
  const [finalPdfUrl, setFinalPdfUrl] = useState("");

  const handleSend = async () => {
    if (!pdfFile) {
      alert("No se ha seleccionado ningún PDF.");
      return;
    }

    let company = "";
    let week = "";
    let pdfName = "";
    try {
      const filename = pdfFile.split("/").pop() || "";
      const parsed = parseFilename(filename);
      company = parsed.company;
      week = parsed.week;
      pdfName = company;
      console.log("Company:", company);
      console.log("Week:", week);
    } catch (error) {
      console.error("Error al extraer company y week:", error);
      alert("El nombre del PDF no cumple el formato esperado.");
      return;
    }

    // Preparamos el FormData para enviar al backend
    const formData = new FormData();
    formData.append('company', company);
    formData.append('week', week);
    formData.append('pdfName', pdfName);

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/finalize', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Error en el proceso");
      }
      // Se espera recibir un JSON con: final_pdf_url, observations y excludes
      const data = await response.json();
      console.log("Datos recibidos:", data);

      // Actualizar el contexto con las observaciones y las páginas a excluir
      if (setObservations) setObservations(data.observations);
      if (setExcludes) setExcludes(data.excludes);

      // Guardar la URL del PDF final para mostrar un enlace de descarga
      setFinalPdfUrl(data.final_pdf_url);
    } catch (error) {
      console.error(error);
      alert("Hubo un error al enviar el reporte");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading ? (
        <Loading />
      ) : (
        <Button
          text="Exportar PDF"
          onClick={handleSend}
          className="mt-4"
          icon={<FileDown size={20} />}
        />
      )}
      {finalPdfUrl && (
        <div className="mt-4">
          <a href={finalPdfUrl} download="final.pdf" className="text-primary underline">
            Descargar PDF Final
          </a>
        </div>
      )}
    </div>
  );
};

export default ExportButton;