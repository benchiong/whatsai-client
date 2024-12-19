import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { TaskArrayType } from "../data-type/task";
import { getTasks } from "../lib/api";
import { useInterval } from "@mantine/hooks";

export type TasksContextType = {
  drawerOpened: boolean;
  setDrawerOpened: (opened: boolean) => void;
  toggleDrawerOpened: () => void;
  tasks: TaskArrayType;
  processingCount: number;
  startLoop: () => void;
  stopLoop: () => void;
};

export const TasksContext = createContext<TasksContextType | null>(null);

export const useTasksContext = () => {
  const context = useContext(TasksContext);
  if (!context) {
    throw new Error("Missing TasksContext.Provider in the tree.");
  }
  return context;
};

export function TasksContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [drawerOpened, setDrawerOpened] = useState(false);
  const [tasks, setTasks] = useState<TaskArrayType>([]);

  const calProcessingTaskCount = useCallback((tasks: TaskArrayType) => {
    let count = 0;
    for (const task of tasks) {
      if (task.status == "processing" || task.status == "queued") {
        count += 1;
      }
    }
    return count;
  }, []);

  const processingCount = calProcessingTaskCount(tasks);
  const emptyCountBeforeStop = useRef(5);

  // when generate/remove task, call start loop
  // then if no processing tasks, then stop loop automatically, avoid looping forever.
  const getLatestTask = useCallback(() => {
    getTasks()
      .then((tasks) => {
        setTasks(tasks);
        const processingTaskCount = calProcessingTaskCount(tasks);

        if (processingTaskCount == 0) {
          if (emptyCountBeforeStop.current <= 0) {
            interval.stop();
            emptyCountBeforeStop.current = 5;
          } else {
            emptyCountBeforeStop.current -= 1;
          }
        }
      })
      .catch((e) => console.error("getTasks failed:", e));
  }, []);

  const interval = useInterval(() => getLatestTask(), 1000);

  useEffect(() => {
    getLatestTask();
  }, []);

  useEffect(() => {
    if (drawerOpened && !interval.active) {
      interval.start();
    }
  }, [drawerOpened]);

  return (
    <TasksContext.Provider
      value={{
        drawerOpened,
        setDrawerOpened,
        toggleDrawerOpened: () => {
          setDrawerOpened(!drawerOpened);
        },
        tasks,
        processingCount,
        startLoop: interval.start,
        stopLoop: interval.stop,
      }}
    >
      {children}
    </TasksContext.Provider>
  );
}
