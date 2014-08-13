#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>
#include <unistd.h>
#include <glib.h>
#include <gio/gio.h>
#include <json-glib/json-glib.h>

static GDBusNodeInfo *introspection_data = NULL;
GHashTable * servos_datax;
GHashTable * servos_datay;

static const gchar introspection_xml[] =
   "<node>"
   "  <interface name='ros3d.kontroler.Interface'>"
   "    <annotation name='ros3d.kontroler.Annotation' value='OnInterface'/>"
   "    <method name='GetStatus'>"
   "      <arg type='s' name='response' direction='out'/>"
   "    </method>"
   "    <method name='SetRange'>"
   "      <arg type='s' name='message' direction='in'/>"
   "      <arg type='s' name='response' direction='out'/>"
   "    </method>"
   "    <method name='GetRange'>"
   "      <arg type='s' name='response' direction='out'/>"
   "    </method>"
   "    <method name='SetPosition'>"
   "      <arg type='s' name='message' direction='in'/>"
   "      <arg type='s' name='response' direction='out'/>"
   "    </method>"
   "    <method name='GetPosition'>"
   "      <arg type='s' name='message' direction='out'/>"
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
        response = g_strdup_printf("[{\"id\": %s, \"position\": %s, \"max\": %s, \"min\": %s}, {\"id\": %s, \"position\": %s, \"max\": %s, \"min\": %s}]", 
                                    g_hash_table_lookup(servos_datax,"id"),
                                    g_hash_table_lookup(servos_datax,"position"),
                                    g_hash_table_lookup(servos_datax,"max"),
                                    g_hash_table_lookup(servos_datax,"min"),
                                    g_hash_table_lookup(servos_datay,"id"),
                                    g_hash_table_lookup(servos_datay,"position"),
                                    g_hash_table_lookup(servos_datay,"max"),
                                    g_hash_table_lookup(servos_datay,"min"));
        g_print("%s\n", response);
        g_dbus_method_invocation_return_value(invocation,
                g_variant_new("(s)", response));
    }
    else if(g_strcmp0(method_name, "GetRange") == 0)
    {
        gchar *response;
        const gchar *message;
        g_variant_get (parameters, "(&s)", &message);
        g_print("%s: %s\n", method_name, message);
        response = g_strdup_printf("!!TBD GetRange %s", message);
        g_dbus_method_invocation_return_value(invocation,
                g_variant_new("(s)", response));
    }
    else if(g_strcmp0(method_name, "SetRange") == 0)
    {
        gchar *response;
        const gchar *message;
        GHashTable *table;
        
        g_variant_get (parameters, "(&s)", &message);
        g_print("message: %s\n", message);
        
        JsonParser *parser = json_parser_new ();
        json_parser_load_from_data (parser, message, -1, NULL);
        JsonReader *reader = json_reader_new (json_parser_get_root (parser));
         
        json_reader_read_member (reader, "id");
        gint id = json_reader_get_int_value (reader);
        json_reader_end_member (reader);
        if(id == 0) //x servo
            table = servos_datax;
        else if(id == 1) //y servo
            table = servos_datay;

        json_reader_read_member (reader, "max");
        gdouble max = json_reader_get_double_value (reader);
        json_reader_end_member (reader);
        g_hash_table_replace(table, "max", g_strdup_printf("%g", max)); 

        json_reader_read_member (reader, "min");
        gdouble min = json_reader_get_double_value (reader);
        json_reader_end_member (reader);
        g_hash_table_replace(table, "min", g_strdup_printf("%g", min)); 

        response = g_strdup_printf("{\"max\": %s, \"min\": %s}", 
                                    g_hash_table_lookup(table,"max"),
                                    g_hash_table_lookup(table,"min"));
        g_dbus_method_invocation_return_value(invocation,
                g_variant_new("(s)", response));
    }
    else if(g_strcmp0(method_name, "SetPosition") == 0)
    {
        gchar *response;
        const gchar *message;
        GHashTable *table;

        g_variant_get (parameters, "(&s)", &message);
        g_print("message: %s\n", message);

        JsonParser *parser = json_parser_new ();
        json_parser_load_from_data (parser, message, -1, NULL);
        JsonReader *reader = json_reader_new (json_parser_get_root (parser));

        json_reader_read_member (reader, "id");
        gint id = json_reader_get_int_value (reader);
        json_reader_end_member (reader);
        if(id == 0) //x servo
            table = servos_datax;
        else if(id == 1) //y servo
            table = servos_datay;

        json_reader_read_member (reader, "position");
        gdouble position = json_reader_get_double_value (reader);
        json_reader_end_member (reader);
        g_hash_table_replace(table, "position", g_strdup_printf("%g", position)); 

        response = g_strdup_printf("{\"position\": %s}", 
                                    g_hash_table_lookup(table,"position"));
        g_dbus_method_invocation_return_value(invocation,
                g_variant_new("(s)", response));
    }
    else if(g_strcmp0(method_name, "GetPosition") == 0)
    {
        gchar *response;
        const gchar *message;
        g_variant_get (parameters, "(&s)", &message);
        g_print("%s: %s\n", method_name, message);
        response = g_strdup_printf("!!TBD GetPosition %s", message);
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

static void init_servos_data()
{
    servos_datax = g_hash_table_new(g_str_hash, g_str_equal);
    g_hash_table_insert(servos_datax, "id", "0");
    g_hash_table_insert(servos_datax, "position", "34");
    g_hash_table_insert(servos_datax, "min", "-200");
    g_hash_table_insert(servos_datax, "max", "320");

    servos_datay = g_hash_table_new(g_str_hash, g_str_equal);
    g_hash_table_insert(servos_datay, "id", "1");
    g_hash_table_insert(servos_datay, "position", "44");
    g_hash_table_insert(servos_datay, "min", "-100");
    g_hash_table_insert(servos_datay, "max", "220");
}

gint main (gint argc, gchar *argv[])
{
    GMainLoop *loop;
    guint id;
    loop = g_main_loop_new(NULL, FALSE);
    init_servos_data();
    //g_print("servosx keys: %d\n", g_hash_table_size(servos_datax));
    //g_print("servosy keys: %d\n", g_hash_table_size(servos_datay));
    g_print("%s\n", g_hash_table_lookup(servos_datax,"id"));
    g_print("%s\n", g_hash_table_lookup(servos_datay,"id"));

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

