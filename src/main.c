#include <stdlib.h>
#include "dbusService.h"
//#include <glib.h>

int main(int argc, char* argv[])
{
    guint owner_id;
    GMainLoop* main_loop = NULL;
    g_type_init();
    main_loop = g_main_loop_new(NULL, FALSE);
    g_timeout_add_seconds(1, callbackHello, "Hello_function");

    GError *error = NULL;
    connection = g_bus_get_sync(G_BUS_TYPE_SESSION, NULL, &error);
    if (error != NULL) {
        syslog(LOG_ERR, "Failed to acquire connection, quitting...\n");
        close(pipefd[1]);
        exit(EXIT_FAILURE);
    } else {
        gchar *conn_name;
        g_object_get(connection, "unique-name", &conn_name, NULL);
        write(pipefd[1], conn_name, strlen(conn_name) + 1);
        close(pipefd[1]);
        g_free(conn_name);
    }
    GDBusNodeInfo *introspection_data = g_dbus_node_info_new_for_xml(introspection_xml, NULL);
    g_assert (introspection_data != NULL);
    GDBusInterfaceInfo *interface_info = g_dbus_node_info_lookup_interface(introspection_data, "dradtke.DBusDaemon");
    owner_id =  g_dbus_connection_register_object(connection,
            "/dradtke/DBusDaemon",
                interface_info,
                &interface_vtable,
                NULL,
                NULL,
                NULL);
    syslog(LOG_NOTICE, "Entering main loop");
    g_main_loop_run(main_loop);

    syslog(LOG_NOTICE, "Exiting...");
    g_main_loop_unref(loop);

    return 0;
}
