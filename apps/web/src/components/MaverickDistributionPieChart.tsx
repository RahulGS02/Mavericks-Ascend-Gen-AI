"use client";

import { useEffect, useRef, useState } from 'react';

interface PieChartData {
  labels: string[];
  values: number[];
  colors: string[];
}

interface MaverickDistributionPieChartProps {
  data: PieChartData;
  compact?: boolean;
}

interface SliceInfo {
  label: string;
  value: number;
  percentage: number;
  startAngle: number;
  endAngle: number;
  color: string;
}

export default function MaverickDistributionPieChart({ data, compact = false }: MaverickDistributionPieChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredSlice, setHoveredSlice] = useState<SliceInfo | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const slicesRef = useRef<SliceInfo[]>([]);

  // Compact mode uses smaller dimensions
  const canvasSize = compact ? 200 : 300;
  const radiusOffset = compact ? 15 : 20;

  useEffect(() => {
    if (!canvasRef.current || !data) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const total = data.values.reduce((sum, val) => sum + val, 0);
    if (total === 0) {
      // Draw empty state
      ctx.fillStyle = '#e5e7eb';
      ctx.font = compact ? '12px Inter, sans-serif' : '14px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No data available', canvas.width / 2, canvas.height / 2);
      return;
    }

    // Calculate percentages
    const percentages = data.values.map(val => (val / total) * 100);

    // Pie chart settings
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - radiusOffset;

    let currentAngle = -Math.PI / 2; // Start from top

    // Store slice information for hover detection
    const slices: SliceInfo[] = [];

    // Draw pie slices
    data.values.forEach((value, index) => {
      const sliceAngle = (value / total) * 2 * Math.PI;
      const endAngle = currentAngle + sliceAngle;

      // Store slice info
      slices.push({
        label: data.labels[index],
        value: value,
        percentage: percentages[index],
        startAngle: currentAngle,
        endAngle: endAngle,
        color: data.colors[index]
      });

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, currentAngle, endAngle);
      ctx.closePath();

      ctx.fillStyle = data.colors[index];
      ctx.fill();

      // Draw border
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      currentAngle = endAngle;
    });

    // Save slices for hover detection
    slicesRef.current = slices;

    // Draw center circle for donut effect
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius * 0.5, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    // Draw total in center
    ctx.fillStyle = '#1e3a8a'; // Blue-900
    ctx.font = compact ? 'bold 18px Inter, sans-serif' : 'bold 24px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(total.toString(), centerX, centerY - (compact ? 6 : 10));
    ctx.font = compact ? '10px Inter, sans-serif' : '12px Inter, sans-serif';
    ctx.fillStyle = '#6b7280';
    ctx.fillText('Total', centerX, centerY + (compact ? 10 : 15));
  }, [data, compact]);

  // Handle mouse move for hover detection
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || slicesRef.current.length === 0) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setMousePos({ x: e.clientX, y: e.clientY });

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Calculate distance from center
    const dx = x - centerX;
    const dy = y - centerY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    const radius = Math.min(centerX, centerY) - 20;
    const innerRadius = radius * 0.5;

    // Check if mouse is within the donut ring
    if (distance >= innerRadius && distance <= radius) {
      // Calculate angle
      let angle = Math.atan2(dy, dx);
      // Normalize angle to match our drawing (starting from top)
      angle = angle + Math.PI / 2;
      if (angle < 0) angle += 2 * Math.PI;

      // Find which slice the mouse is over
      const slice = slicesRef.current.find(s => {
        let start = s.startAngle;
        let end = s.endAngle;

        // Normalize angles
        while (start < 0) start += 2 * Math.PI;
        while (end < 0) end += 2 * Math.PI;
        while (angle < start) angle += 2 * Math.PI;

        return angle >= start && angle <= end;
      });

      setHoveredSlice(slice || null);
    } else {
      setHoveredSlice(null);
    }
  };

  const handleMouseLeave = () => {
    setHoveredSlice(null);
  };

  if (!data || data.values.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No data available
      </div>
    );
  }

  const total = data.values.reduce((sum, val) => sum + val, 0);

  return (
    <div className={compact ? "relative" : "space-y-4 relative"}>
      {/* Canvas and Legend Side by Side for Compact Mode */}
      <div className={compact ? "flex items-center gap-4" : "space-y-4"}>
        {/* Canvas */}
        <div className={compact ? "flex-shrink-0" : "flex justify-center relative"}>
          <canvas
            ref={canvasRef}
            width={canvasSize}
            height={canvasSize}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            className="cursor-pointer"
          />

          {/* Hover Tooltip */}
          {hoveredSlice && (
            <div
              className="fixed z-50 bg-gray-900 text-white px-2 py-1.5 rounded shadow-lg text-xs pointer-events-none"
              style={{
                left: `${mousePos.x + 10}px`,
                top: `${mousePos.y - 10}px`,
              }}
            >
              <div className="font-bold text-sm">{hoveredSlice.label}</div>
              <div className="text-xs opacity-90">
                {hoveredSlice.value} ({hoveredSlice.percentage.toFixed(1)}%)
              </div>
            </div>
          )}
        </div>

        {/* Legend with Counts */}
        <div className={compact ? "flex-1 space-y-2" : "grid grid-cols-2 gap-2"}>
          {data.labels.map((label, index) => (
            <div
              key={index}
              className="flex items-center justify-between gap-3"
            >
              <div className="flex items-center gap-1.5">
                <div
                  className={compact ? "w-2.5 h-2.5 rounded-full flex-shrink-0" : "w-3 h-3 rounded-full flex-shrink-0"}
                  style={{ backgroundColor: data.colors[index] }}
                />
                <p className={compact ? "text-xs font-medium text-gray-700" : "text-xs font-medium text-gray-700"}>
                  {label}
                </p>
              </div>
              <div className={compact ? "text-sm font-bold text-blue-900" : "text-xs font-semibold text-blue-900"}>
                {data.values[index]}
              </div>
            </div>
          ))}
        </div>
      </div>

      {!compact && (
        <p className="text-xs text-center text-gray-500 italic">
          Hover over chart to see details
        </p>
      )}
    </div>
  );
}
