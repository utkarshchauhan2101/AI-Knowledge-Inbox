import { useCallback, useEffect, useState } from "react";
import AddItem from "./components/AddItem";
import ItemList from "./components/ItemList";
import AskBox from "./components/AskBox";
import { api } from "./api";

export default function App() {
  const [items, setItems] = useState([]);

  const refresh = useCallback(async () => {
    try {
      setItems(await api.listItems());
    } catch (e) {
      console.error("failed to load items", e);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="mx-auto max-w-2xl space-y-6 p-6">
      <h1 className="text-2xl font-bold">Notes RAG</h1>
      <AddItem onAdded={refresh} />
      <ItemList items={items} />
      <AskBox />
    </div>
  );
}
