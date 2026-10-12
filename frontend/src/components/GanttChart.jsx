import { useId, useState } from "react";

const CHART_WIDTH = 980;
const LABEL_WIDTH = 260;
const RIGHT_PADDING = 28;
const TOP_PADDING = 66;
const ROW_HEIGHT = 48;
const BAR_HEIGHT = 22;
const TOOLTIP_WIDTH = 220;
const TOOLTIP_HEIGHT = 96;

function formatValue(value) {
  return value ?? "—";
}

export default function GanttChart({ data = [] }) {
  const [activeId, setActiveId] = useState(null);
  const patternId = `gantt-critical-${useId().replace(/:/g, "")}`;
  const tasks = Array.isArray(data) ? data : [];
  const chartAreaWidth = CHART_WIDTH - LABEL_WIDTH - RIGHT_PADDING;
  const maxDay = Math.max(1, ...tasks.flatMap(task => [Number(task.ef) || 0, Number(task.lf) || 0]));
  const domainEnd = Math.ceil(maxDay / 5) * 5 || 5;
  const xForDay = day => LABEL_WIDTH + (Number(day) / domainEnd) * chartAreaWidth;
  const chartHeight = TOP_PADDING + tasks.length * ROW_HEIGHT + 124;
  const tickStep = domainEnd <= 20 ? 1 : 5;
  const ticks = Array.from({ length: Math.floor(domainEnd / tickStep) + 1 }, (_, index) => index * tickStep);

  return (
    <div style={{ overflowX: "auto", width: "100%" }}>
      <svg
        aria-label="Biểu đồ Gantt tiến độ công việc"
        role="img"
        viewBox={`0 0 ${CHART_WIDTH} ${chartHeight}`}
       style={{ display: "block", maxWidth: 980, width: "100%", fontFamily: "inherit" }}
      >
        <defs>
          <pattern id={patternId} width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="8" height="8" fill="#fff1ed" />
            <line x1="0" y1="0" x2="0" y2="8" stroke="#c74732" strokeWidth="3" />
          </pattern>
        </defs>

        <text x={LABEL_WIDTH} y="25" fill="#526158" fontSize="12" fontWeight="600">
          Thời gian (ngày)
        </text>
        <rect x={LABEL_WIDTH} y="39" width="18" height="12" rx="2" fill={`url(#${patternId})`} stroke="#a83424" strokeWidth="2" />
        <text x={LABEL_WIDTH + 25} y="49" fill="#526158" fontSize="11">Công việc găng</text>

        {ticks.map(tick => {
          const x = xForDay(tick);
          return (
            <g key={tick}>
              <line x1={x} y1={TOP_PADDING - 10} x2={x} y2={chartHeight - 45} stroke="#e5ece8" />
              <text x={x} y={TOP_PADDING - 18} textAnchor="middle" fill="#718078" fontSize="10">{tick}</text>
            </g>
          );
        })}

        {tasks.map((task, index) => {
          const rowY = TOP_PADDING + index * ROW_HEIGHT;
          const barY = rowY + (ROW_HEIGHT - BAR_HEIGHT) / 2;
          const startX = xForDay(task.es);
          const endX = xForDay(task.ef);
          const barWidth = Math.max(endX - startX, 2);
          const isActive = activeId === task.id;
          const label = `${task.name}: ES ${formatValue(task.es)}, EF ${formatValue(task.ef)}, LS ${formatValue(task.ls)}, LF ${formatValue(task.lf)}, độ trễ ${formatValue(task.totalFloat)} ngày${task.isCritical ? ", công việc găng" : ""}`;
          const tooltipX = Math.min(
            Math.max(startX + barWidth / 2 - TOOLTIP_WIDTH / 2, LABEL_WIDTH),
            CHART_WIDTH - RIGHT_PADDING - TOOLTIP_WIDTH,
          );
          const aboveY = barY - TOOLTIP_HEIGHT - 10;
        const belowY = barY + BAR_HEIGHT + 10;
const nextRowHasBar = index < tasks.length - 1;
const tooltipY = (aboveY >= TOP_PADDING + 10 || nextRowHasBar) ? aboveY : belowY;
          const fill = task.isCritical ? `url(#${patternId})` : "#20a16b";
          const stroke = task.isCritical ? "#a83424" : "#08794f";
          const tipId = `${patternId}-tip-${index}`;

          return (
            <g key={task.id}>
              <line x1={LABEL_WIDTH} y1={rowY + ROW_HEIGHT} x2={CHART_WIDTH - RIGHT_PADDING} y2={rowY + ROW_HEIGHT} stroke="#f0f3f1" />
              <text x="8" y={barY + BAR_HEIGHT / 2 + 4} fill="#34453d" fontSize="11">{task.name}</text>
              <g
                role="button"
                tabIndex={0}
                aria-label={label}
                aria-describedby={isActive ? tipId : undefined}
                onPointerEnter={event => {
                  if (event.pointerType !== "touch") setActiveId(task.id);
                }}
                onPointerLeave={event => {
                  if (event.pointerType !== "touch" && !event.currentTarget.matches(":focus-within")) {
                    setActiveId(current => current === task.id ? null : current);
                  }
                }}
                onFocus={() => setActiveId(task.id)}
                onBlur={() => setActiveId(current => current === task.id ? null : current)}
                onClick={() => setActiveId(current => current === task.id ? null : task.id)}
                onKeyDown={event => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    setActiveId(current => current === task.id ? null : task.id);
                  }
                  if (event.key === "Escape") setActiveId(null);
                }}
                style={{ cursor: "pointer", outline: "none" }}
              >
                <rect
                  x={startX}
                  y={barY}
                  width={barWidth}
                  height={BAR_HEIGHT}
                  rx="4"
                  fill={fill}
                  stroke={stroke}
                  strokeWidth={task.isCritical ? 3 : 1.5}
                />
                <rect
                  x={startX - 5}
                  y={barY - 5}
                  width={barWidth + 10}
                  height={BAR_HEIGHT + 10}
                  fill="transparent"
                  stroke="transparent"
                />
              </g>

              {isActive && (
                <g id={tipId} role="tooltip" pointerEvents="none">
                  <rect x={tooltipX} y={tooltipY} width={TOOLTIP_WIDTH} height={TOOLTIP_HEIGHT} rx="7" fill="#102d26" />
                  <text x={tooltipX + 12} y={tooltipY + 19} fill="white" fontSize="11" fontWeight="700">{task.name}</text>
                  <text x={tooltipX + 12} y={tooltipY + 38} fill="#e1eee7" fontSize="10">
                    ES: {formatValue(task.es)} · EF: {formatValue(task.ef)}
                  </text>
                  <text x={tooltipX + 12} y={tooltipY + 55} fill="#e1eee7" fontSize="10">
                    LS: {formatValue(task.ls)} · LF: {formatValue(task.lf)}
                  </text>
                  <text x={tooltipX + 12} y={tooltipY + 74} fill="#e1eee7" fontSize="10">
                    Độ trễ: {formatValue(task.totalFloat)} ngày
                  </text>
                  <text x={tooltipX + 12} y={tooltipY + 89} fill="#e1eee7" fontSize="9">
                    {task.isCritical ? "Công việc găng" : "Không găng"}
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
