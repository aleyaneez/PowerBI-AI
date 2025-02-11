import React from 'react';
import { CircleCheck } from 'lucide-react';
import Button from './Button';

interface ApproveProps {
  onClick?: () => void;
}

const Approve: React.FC<ApproveProps> = ({ onClick }) => {
  return (
    <Button
      text=""
      onClick={onClick}
      className="px-2 py-2"
      icon={<CircleCheck size={16} />}
      title="Aprobar observación"
    />
  );
};

export default Approve;