#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>
#include <unistd.h>
#include <glib.h>
#include <gio/gio.h>

static GDBusNodeInfo *introspection_data = NULL;
static const gchar introspection_xml[] =
   "<node>"
   "  <interface name='ros3d.kontroler.Interface'>"
   "    <annotation name='ros3d.kontroler.Annotation' value='OnInterface'/>"
   "    <method name='GetStatus'>"
   "      <arg type='s' name='response' direction='out'/>"
   "    </method>"
   "    <method name='GetRange'>"
   "      <arg type='s' name='message' direction='in'/>"
   "      <arg type='s' name='response' direction='out'/>"
   "    </method>"
   "    <method name='GetPosition'>"
   "      <arg type='s' name='message' direction='in'/>"
   "      <arg type='s' name='response' direction='out'/>"
   "    </method>"
   "  </interface>"
   "</node>";

static void handle_method_call (GDBusConnection       *connection,
        const gchar           *sender,
        const gchar           *object_path,
        const gchar           *interface_name,
        const gchar           *method_name,
        GVariant              *parameters,
        GDBusMethodInvocation *invocation,
        gpointer               user_data)
{
    if(g_strcmp0(method_name, "GetStatus") == 0)
    {
        gchar *response;
        const gchar *message;
        //g_variant_get (parameters, "(&s)", &message);
        g_print("%s\n", method_name);
        message = "test";
        response = g_strdup_printf("[%s:%s]", message, message);
        g_dbus_method_invocation_return_value(invocation,
                g_variant_new("(s)", response));
    }
    else if(g_strcmp0(method_name, "GetRange") == 0)
    {
        gchar *response;
        const gchar *message;
        g_variant_get (parameters, "(&s)", &message);
        g_print("%s: %s\n", method_name, message);
        response = g_strdup_printf("GetRange %s", message);
        g_dbus_method_invocation_return_value(invocation,
                g_variant_new("(s)", response));
    }
    else if(g_strcmp0(method_name, "GetPosition") == 0)
    {
        gchar *response;
        const gchar *message;
        g_variant_get (parameters, "(&s)", &message);
        g_print("%s: %s\n", method_name, message);
        response = g_strdup_printf("GetRange %s", message);
        g_dbus_method_invocation_return_value(invocation,
                g_variant_new("(s)", response));
    }
    else g_print("else method_handler\n");
}

static gboolean handle_set_property (GDBusConnection  *connection,
        const gchar      *sender,
        const gchar      *object_path,
        const gchar      *interface_name,
        const gchar      *property_name,
        GVariant         *value,
        GError          **error,
        gpointer          user_data)
{
    g_print("set property\n");
    g_set_error (error,
            G_IO_ERROR,
            G_IO_ERROR_FAILED,
            "Hello AGAIN %s. I thought I said writing this property "
            "always results in an error. kthxbye",
            sender);

    return *error = NULL;
}

static GVariant *handle_get_property (GDBusConnection  *connection,
        const gchar      *sender,
        const gchar      *object_path,
        const gchar      *interface_name,
        const gchar      *property_name,
        GError          **error,
        gpointer          user_data)
{
    g_print("get property\n");
    GVariant *ret;
    return ret;
}

static const GDBusInterfaceVTable interface_vtable =
{
    handle_method_call,
    handle_get_property,
    handle_set_property
};

static void on_bus_acquired (GDBusConnection *connection,
        const gchar     *name,
        gpointer         user_data)
{
    guint registration_id;
    g_print("on_bus_acquired\n");
    registration_id = g_dbus_connection_register_object (connection,
            "/ros3d/kontroler/Object",
            introspection_data->interfaces[0],
            &interface_vtable,
            NULL,  /* user_data */
            NULL,  /* user_data_free_func */
            NULL); /* GError** */
    g_assert (registration_id > 0);
    g_print("on_bus_acquired end\n");
}

static void on_name_acquired (GDBusConnection *connection,
        const gchar     *name,
        gpointer         user_data)
{
    g_print ("Acquired the name %s\n", name);
}

static void on_name_lost(GDBusConnection *connection,
        const gchar     *name,
        gpointer         user_data)
{
    g_print ("Lost the name %s\n", name);
}

gint main (gint argc, gchar *argv[])
{
    GMainLoop *loop;
    guint id;
    loop = g_main_loop_new(NULL, FALSE);


    introspection_data = g_dbus_node_info_new_for_xml(introspection_xml, NULL);
    g_assert(introspection_data != NULL);

    //id = g_bus_own_name(G_BUS_TYPE_SESSION,
    id = g_bus_own_name(G_BUS_TYPE_SYSTEM,
            "ros3d.kontroler.Server",
            G_BUS_NAME_OWNER_FLAGS_ALLOW_REPLACEMENT,
            on_bus_acquired,
            on_name_acquired,
            on_name_lost,
            NULL,
            NULL);

    g_main_loop_run(loop);
    g_bus_unown_name(id);
    g_main_loop_unref(loop);

    return 0;
}

