import { useEffect, useRef, useState, type ReactNode } from "react";

interface ChartContainerProps {
  children: (width: number) => ReactNode;
}

export function ChartContainer({ children }: ChartContainerProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setWidth(entry.contentRect.width);
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} style={{ width: "100%", minHeight: 300 }}>
      {width > 0 ? children(width) : null}
    </div>
  );
}
