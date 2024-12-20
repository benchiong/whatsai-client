/* make it easier to debug.
   Why we need those?
   frontend depends on a exe file from packed manager, it's in the assets by default no matter it's dev or prod env
   so we you want to debug it, you can not debug the exe file.
  
   Debug Manager(means the manager starts, and also start backend server automatically):
    1.set debug_manager = true
    2.start backend-manager (backend-manager dir) with python main.py, get the url and set it to
      debug_manager_url manually
    
   Debug Backend Server(means no manager's work at all, you start the backend server manually)
    1.set debug_backend = true
    2.start backend server(backend dir) and python main.py, get the url and set it to
      debug_backend_server_url manually
 */
export const debug_manager = true;
export const debug_manager_url = "http://127.0.0.1:8820/";

export const debug_backend = false;
export const debug_backend_server_url = "http://127.0.0.1:8172/";
