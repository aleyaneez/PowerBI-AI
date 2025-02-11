import React from 'react';
import { RefreshCcw } from 'lucide-react';
import Button from './Button';

interface RegenerateProps {
  onClick?: () => void;
}

const Regenerate: React.FC<RegenerateProps> = ({ onClick }) => {
  return (
    <Button
      text=""
      onClick={onClick}
      className="px-2 py-2"
      icon={<RefreshCcw size={16} />}
      title="Regenerar observación"
    />
  );
};

export default Regenerate;