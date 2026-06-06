import { useRef, useState, useEffect, type ReactNode } from "react";

interface Props {
  children: (w: number, h: number) => ReactNode;
  height: number;
}

export default function ChartContainer({ children, height }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(() => {
      if (el.clientWidth > 0) setReady(true);
    });
    ro.observe(el);
    if (el.clientWidth > 0) setReady(true);
    return () => ro.disconnect();
  }, []);

  return (
    <div ref={ref} style={{ width: "100%", minHeight: height, position: "relative" }}>
      {ready && children(ref.current?.clientWidth ?? 800, height)}
    </div>
  );
}
