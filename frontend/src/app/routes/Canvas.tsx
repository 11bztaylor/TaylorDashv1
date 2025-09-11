import { useEffect, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Background,
  Controls,
  Connection,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { T } from '../../lib/tokens';

const INITIAL_NODES: Node[] = [
  {
    id: '1',
    type: 'default',
    position: { x: 250, y: 25 },
    data: { label: 'Start' },
  },
  {
    id: '2',
    type: 'default',
    position: { x: 100, y: 125 },
    data: { label: 'Process A' },
  },
  {
    id: '3',
    type: 'default',
    position: { x: 400, y: 125 },
    data: { label: 'Process B' },
  },
  {
    id: '4',
    type: 'default',
    position: { x: 250, y: 225 },
    data: { label: 'End' },
  },
];

const INITIAL_EDGES: Edge[] = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e1-3', source: '1', target: '3' },
  { id: 'e2-4', source: '2', target: '4' },
  { id: 'e3-4', source: '3', target: '4' },
];

const STORAGE_KEY = 'td.canvas.v1';

export function Canvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState(INITIAL_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState(INITIAL_EDGES);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const { nodes: savedNodes, edges: savedEdges } = JSON.parse(saved);
        setNodes(savedNodes || INITIAL_NODES);
        setEdges(savedEdges || INITIAL_EDGES);
      } catch (error) {
        console.error('Failed to parse saved canvas data:', error);
      }
    }
  }, [setNodes, setEdges]);

  // Save to localStorage when nodes or edges change
  useEffect(() => {
    const canvasData = { nodes, edges };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(canvasData));
  }, [nodes, edges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Canvas</h1>
      
      <div className={`h-[72vh] rounded-2xl ${T.card} ${T.ring} ring-1`}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          style={{ borderRadius: '1rem' }}
          attributionPosition="bottom-left"
        >
          <Background variant={BackgroundVariant.Dots} />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}