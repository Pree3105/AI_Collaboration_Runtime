interface Props {
  onClick: () => void;
  label?: string;
  disabled?: boolean;
}

export default function ExecuteButton({ onClick, label = "Execute", disabled }: Props): JSX.Element {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={(event) => {
        event.stopPropagation();
        onClick();
      }}
      className="rounded-md bg-blue-600 text-white text-xs font-medium px-3 py-1.5 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
    >
      {label}
    </button>
  );
}
