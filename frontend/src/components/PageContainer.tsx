import React, { useContext, useState } from 'react';
import { PDFContext } from '../context/PDFContext';
import ObservationCard from './ObservationCard';
import Loading from './Loading';

interface PageContainerProps {
  pageNumber: number;
  pngUrl: string;
  observation: string;
  excluded: boolean;
}

const PageContainer: React.FC<PageContainerProps> = ({
  pageNumber,
  pngUrl,
  observation,
  excluded
}) => {
  const {
    observations,
    setObservations,
    company,
    week,
    pdfName,
  } = useContext(PDFContext);
  const [isRegenerating, setIsRegenerating] = useState(false);

  // Aprobar
  const handleApprove = () => {
    setObservations(prev =>
      prev.map(obs =>
        obs.pageNumber === pageNumber
          ? { ...obs, approved: !obs.approved }
          : obs
      )
    );
    console.log(`Observación de página ${pageNumber} aprobada`);
  };

  const handleEdit = (newValue: string) => {
    setObservations(prev =>
      prev.map(obs =>
        obs.pageNumber === pageNumber
          ? { ...obs, observation: newValue, approved: false }
          : obs
      )
    );
    console.log(`Observación de página ${pageNumber} editada:`, newValue);
  };

  // Eliminar
  const handleDelete = () => {
    setObservations(prev =>
      prev.map(obs =>
        obs.pageNumber === pageNumber
          ? { ...obs, observation: "", approved: false }
          : obs
      )
    );
    console.log(`Observación de página ${pageNumber} eliminada`);
  };

  // Regenerar
  const handleRegenerate = async () => {
    try {
      setIsRegenerating(true);
      const formData = new FormData();
      formData.append("company", company);
      console.log("Company:", company);
      formData.append("week", week);
      console.log("Week:", week);
      formData.append("pdfName", pdfName);
      console.log("PdfName:", pdfName);
      formData.append("pageNumber", pageNumber.toString());

      const res = await fetch("http://localhost:8000/regenerate-observation", {
        method: "POST",
        body: formData
      });
      if (!res.ok) throw new Error("Error al regenerar observación");

      const data = await res.json();
      setObservations(prev =>
        prev.map(obs =>
          obs.pageNumber === data.pageNumber
            ? { ...obs, observation: data.newObservation, approved: false }
            : obs
        )
      );
      console.log(`Observación de página ${pageNumber} regenerada`);
    } catch (error) {
      console.error(error);
      alert("Error al regenerar la observación.");
    } finally {
      setIsRegenerating(false);
    }
  };

  const obsData = observations.find(obs => obs.pageNumber === pageNumber);
  const isApproved = obsData?.approved ?? false;

  return (
    <div className="min-w-[300px]">
      <h3 className="text-center font-semibold text-tertiary mb-1">
        Página {pageNumber}
      </h3>
      <div className="p-2 flex justify-center items-center">
        <img
          src={pngUrl}
          alt={`Página ${pageNumber}`}
          width={900}
          className="border rounded-sm border-slate-400"
        />
      </div>
      {!excluded && (
        isRegenerating ? (
          <div className="flex flex-col mt-12 justify-center items-center space-y-4">
            <h4 className="text-base text-primary font-semibold">Regenerando observación...</h4>
            <Loading
              color="#283575"
              size={8}
            />
          </div>
        ) : (
          <ObservationCard
            observation={observation}
            approved={isApproved}
            onApprove={handleApprove}
            onDelete={handleDelete}
            onRegenerate={handleRegenerate}
            onEdit={handleEdit}
          />
        )
      )}
    </div>
  );
};

export default PageContainer;