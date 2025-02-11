import React from 'react';
import Approve from './Approve';
import Regenerate from './Regenerate';
import Delete from './Delete';

interface ObservationCardProps {
  observation: string;
  onApprove?: () => void;
  onRegenerate?: () => void;
  onDelete?: () => void;
}

const ObservationCard: React.FC<ObservationCardProps> = ({ observation, onApprove, onRegenerate, onDelete }) => {
  return (
    <div className="flex flex-row items-center mt-4 justify-between">
      <div className="p-4 border rounded-xl border-slate-400 h-28">
        <p className="text-sm text-primary">{observation || "Sin observación"}</p>
      </div>
      <div className="flex flex-col items-center justify-center gap-1 ml-4">
        <Approve onClick={onApprove} />
        <Delete onClick={onDelete} />
        <Regenerate onClick={onRegenerate} />
      </div>
    </div>
  );
};

export default ObservationCard;