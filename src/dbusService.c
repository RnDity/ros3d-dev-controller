#include "dbusService.h"

static GDBusNodeInfo *introspection_data = NULL;
static const gchar introspection_xml[] =
    "<node>"
    "  <interface name='ros3d.ServoDaemon'>"
    "    <method name='SendMessage'>"
    "      <arg type='s' name='message' direction='in'/>"
    "      <arg type='s' name='response' direction='out'/>"
    "    </method>"
    "  </interface>"
    "</node>";

static const GDBusInterfaceVTable interface_vtable = {
    &handle_method_call,
    &handle_get_property,
    &handle_set_property
};


static void handle_method_call(GDBusConnection *conn,
        const gchar *sender,
        const gchar *object_path,
        const gchar *interface_name,
        const gchar *method_name,
        GVariant *parameters,
        GDBusMethodInvocation *invocation,
        gpointer user_data)
{
        if (!g_strcmp0(method_name, "SendMessage")) 
        {
            gchar *message;
            gchar *response;
            g_variant_get(parameters, "(s)", &message);
            response = g_strdup_printf("Received message: %s", message);
            g_dbus_method_invocation_return_value(invocation, g_variant_new("(s)", response));
            g_free(message);
            g_free(response);
        }
}

static GVariant *handle_get_property(GDBusConnection *conn,
        const gchar *sender,
        const gchar *object_path,
        const gchar *interface_name,
        const gchar *property_name,
        GError **error,
        gpointer user_data)
{
    return NULL;
}

static gboolean handle_set_property(GDBusConnection *conn,
        const gchar *sender,
        const gchar *object_path,
        const gchar *interface_name,
        const gchar *property_name,
        GVariant *value,
        GError **error,
        gpointer user_data)
{
    return FALSE;
}

static void cleanup()
{
    closelog();
}

static void sig_handler(int signo)
{
    if (signo == SIGINT) {
        g_main_loop_quit(loop);
    }
}

int main(int argc, char* argv[])
{
    guint owner_id;
    GMainLoop* main_loop = NULL;
    #if !defined(GLIB_VERSION_2_36)
        g_type_init();
    #endif
    main_loop = g_main_loop_new(NULL, FALSE);
    //g_timeout_add_seconds(10, callbackHello, "Hello_function");

    GError *error = NULL;
    connection = g_bus_get_sync(G_BUS_TYPE_SYSTEM, NULL, &error);
    if (error != NULL) {
        syslog(LOG_ERR, "Failed to acquire connection, quitting...\n");
        printf("Failed to acquire connection, quitting...\n");
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
    GDBusInterfaceInfo *interface_info = g_dbus_node_info_lookup_interface(introspection_data, "ros3d.ServoDaemon");
    owner_id =  g_dbus_connection_register_object(connection,
            "/ros3d/ServoDaemon",
                interface_info,
                &interface_vtable,
                NULL,
                NULL,
                NULL);
    syslog(LOG_NOTICE, "Entering main loop");
    printf("Entering main loop\n");
    g_main_loop_run(main_loop);

    syslog(LOG_NOTICE, "Exiting...");
    printf("Exiting...\n");
    g_main_loop_unref(loop);

    return 0;
}

int printHello()
{
    printf("Hello world\n");
}

gboolean callbackHello(gpointer data)
{
    printf("Hello %s\n", (char*)data);
    return TRUE;
}


