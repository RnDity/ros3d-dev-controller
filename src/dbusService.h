
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>
#include <unistd.h>
#include <glib.h>
#include <gio/gio.h>

int printHello();
gboolean callbackHello();

static GDBusNodeInfo *introspection_data;
static const gchar introspection_xml[];
static int pipefd[2];
static GMainLoop *loop;
static GDBusConnection *connection;
static void handle_method_call(GDBusConnection *conn,
        const gchar *sender,
        const gchar *object_path,
        const gchar *interface_name,
        const gchar *method_name,
        GVariant *parameters,
        GDBusMethodInvocation *invocation,
        gpointer user_data);
static GVariant *handle_get_property(GDBusConnection *conn,
        const gchar *sender,
        const gchar *object_path,
        const gchar *interface_name,
        const gchar *property_name,
        GError **error,
        gpointer user_data);
static gboolean handle_set_property(GDBusConnection *conn,
        const gchar *sender,
        const gchar *object_path,
        const gchar *interface_name,
        const gchar *property_name,
        GVariant *value,
        GError **error,
        gpointer user_data);
static void cleanup();
static void daemonize(char *name);
static void sig_handler(int signo);

