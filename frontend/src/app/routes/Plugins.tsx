import { PLUGINS } from "../../plugins/registry";

export default function Plugins(){
  return (
    <ul className="space-y-2">
      {PLUGINS.map(p=> (
        <li key={p.id}>
          <a className="underline" href={p.path}>{p.name}</a>
        </li>
      ))}
    </ul>
  );
}