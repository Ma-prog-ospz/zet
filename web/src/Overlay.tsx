import { useEffect } from "react";
import "./Overlay.css";

interface OverlayProps {
  onClose: () => void;
  children: React.ReactNode;
  onBackgroundClick?: (e: React.MouseEvent) => void;
  verticalPosition?: "middle" | "bottom";
}

export function Overlay({
  onClose,
  children,
  onBackgroundClick,
  verticalPosition = "middle",
}: OverlayProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [onClose]);

  const handleBackgroundClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget && onBackgroundClick) {
      onBackgroundClick(e);
    } else if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const verticalPositionClass =
    verticalPosition === "bottom" ? "overlay-content-bottom" : "";

  return (
    <div className="overlay" onClick={handleBackgroundClick}>
      <div className={`overlay-content ${verticalPositionClass}`}>
        <button className="overlay-close-button" onClick={onClose}>
          ✕
        </button>
        {children}
      </div>
    </div>
  );
}
