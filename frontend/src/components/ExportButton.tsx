import React, { useContext, useState } from 'react';
import { PDFContext } from '../context/PDFContext';
import Button from './Button';
import { FileDown } from 'lucide-react';
import { parseFilename } from '../utils/parseFilename';
import Loading from './Loading';

const ExportButton: React.FC = () => {
  const { pdfFile } = useContext(PDFContext);
  const [loading, setLoading] = useState(false);

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
      const blob = await response.blob();
      // Forzar la descarga del PDF final
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "final.pdf";
      a.click();
      window.URL.revokeObjectURL(url);
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
    </div>
  );
};

export default ExportButton;