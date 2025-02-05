import React, { useContext } from 'react';
import { PDFContext } from '../context/PDFContext';
import Button from './Button';
import { FileDown } from 'lucide-react';

const ExportButton: React.FC = () => {
  const { pdfFile, observations } = useContext(PDFContext);

  const handleSend = async () => {
    // Verifica que todas las páginas estén aprobadas
    const notApproved = observations.filter(page => !page.approved);
    if (notApproved.length > 0) {
      alert("Por favor, aprueba todas las observaciones antes de enviar.");
      return;
    }

    // Prepara el objeto con las observaciones: { "1": "Obs página 1", ... }
    const obsData: Record<number, string> = {};
    observations.forEach(page => {
      obsData[page.pageNumber] = page.observation;
    });

    if (!pdfFile) {
      alert("No se ha seleccionado ningún PDF.");
      return;
    }

    // Aquí debes definir o extraer los demás parámetros
    const company = "abastible"; // o extraer del estado/contexto
    const week = "2025-01-20";    // idem
    const pdfName = "Abastible";  // idem
    const excludePages = [0, 7, 8, 21, 35];
    const riesgo = { "bajo": 6.1, "medio": 8.2, "alto": 9.8 };

    const formData = new FormData();
    formData.append('file', pdfFile);
    formData.append('observations', JSON.stringify(obsData));
    formData.append('company', company);
    formData.append('week', week);
    formData.append('pdfName', pdfName);
    formData.append('excludePages', JSON.stringify(excludePages));
    formData.append('riesgo', JSON.stringify(riesgo));

    try {
      const response = await fetch('http://localhost:8000/finalize', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Error en el proceso");
      }
      const blob = await response.blob();
      // Descargar el PDF final
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "final.pdf";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      alert("Hubo un error al enviar el reporte");
    }
  };

  return (
    <Button
      text="Exportar PDF"
      onClick={handleSend}
      className="mt-4"
      icon={<FileDown size={20} />}
    />
  );
};

export default ExportButton;