/* Count PyObject allocations while active. Loaded by the intake harnesses. */
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static unsigned long long alloc_count = 0;
static int active = 0;
static PyMemAllocatorEx orig_obj;

static void *hook_malloc(void *ctx, size_t size) {
    if (active) {
        alloc_count++;
    }
    return orig_obj.malloc(orig_obj.ctx, size);
}

static void *hook_calloc(void *ctx, size_t nelem, size_t elsize) {
    if (active) {
        alloc_count++;
    }
    return orig_obj.calloc(orig_obj.ctx, nelem, elsize);
}

static void *hook_realloc(void *ctx, void *ptr, size_t new_size) {
    if (active) {
        alloc_count++;
    }
    return orig_obj.realloc(orig_obj.ctx, ptr, new_size);
}

static void hook_free(void *ctx, void *ptr) {
    orig_obj.free(orig_obj.ctx, ptr);
}

static PyObject *py_start(PyObject *self, PyObject *args) {
    alloc_count = 0;
    active = 1;
    Py_RETURN_NONE;
}

static PyObject *py_stop(PyObject *self, PyObject *args) {
    active = 0;
    return PyLong_FromUnsignedLongLong(alloc_count);
}

static PyMethodDef methods[] = {
    {"start", py_start, METH_NOARGS, NULL},
    {"stop", py_stop, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "alloccount",
    NULL,
    -1,
    methods,
};

PyMODINIT_FUNC PyInit_alloccount(void) {
    PyMemAllocatorEx alloc;

    PyMem_GetAllocator(PYMEM_DOMAIN_OBJ, &orig_obj);
    alloc.ctx = NULL;
    alloc.malloc = hook_malloc;
    alloc.calloc = hook_calloc;
    alloc.realloc = hook_realloc;
    alloc.free = hook_free;
    PyMem_SetAllocator(PYMEM_DOMAIN_OBJ, &alloc);
    return PyModule_Create(&moduledef);
}
