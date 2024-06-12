/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */


template<class K, class V, class U> static inline void __add_to_dict(dict<K, V> *d, U *iter) {
    __iter<typename U::for_in_unit> *it = ___iter(iter);
    typename U::for_in_unit a, b;
    a = it->__next__();
    b = it->__next__();
    d->__setitem__(a, b);
}

template<class K, class V> static inline void __add_to_dict(dict<K, V> *d, tuple2<K, V> *t) {
    d->__setitem__(t->__getfirst__(), t->__getsecond__());
}

template<class K, class V> dict<K,V>::dict() {
    this->__class__ = cl_dict;
}

template<class K, class V> template<class ... Args> dict<K, V>::dict(int count, Args ... args)  {
    this->__class__ = cl_dict;

    (__add_to_dict(this, args), ...);
}

template<class K, class V> template<class U> dict<K, V>::dict(U *other) {
    this->__class__ = cl_dict;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,other,1,2,3)
        __add_to_dict(this, e);
    END_FOR
}

template<class K, class V> dict<K, V>::dict(dict<K, V> *p)  {
    this->__class__ = cl_dict;

    *this = *p;
}

#ifdef __SS_BIND
template<class K, class V> dict<K, V>::dict(PyObject *p) {
    if(!PyDict_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (dictionary expected)"));

    this->__class__ = cl_dict;
    PyObject *key, *value;

    PyObject *iter = PyObject_GetIter(p);
    while ((key = PyIter_Next(iter))) {
        value = PyDict_GetItem(p, key);
        __setitem__(__to_ss<K>(key), __to_ss<V>(value));
        Py_DECREF(key);
    }
    Py_DECREF(iter);
}

template<class K, class V> PyObject *dict<K, V>::__to_py__() {
   PyObject *p = PyDict_New();

   for (const auto& [key, value] : gcd) {
       PyObject *pkey = __to_py(key);
       PyObject *pvalue = __to_py(value);
       PyDict_SetItem(p, pkey, pvalue);
       Py_DECREF(pkey);
       Py_DECREF(pvalue);
   }

   return p;
}
#endif

template<class K, class V> __ss_bool dict<K,V>::__eq__(pyobj *p) {
    dict<K,V> *b = (dict<K,V> *)p;

    if(b->__len__() != this->__len__())
        return False;

    // TODO why can't we just use unordered_map operator==
    typename __GC_DICT<K, V>::iterator it;

    for (const auto& [key, value] : gcd) {
        it = b->gcd.find(key);
        if(it == b->gcd.end())
            return False;
        else if(__ne((*it).second, value))
            return False;
    }

    return True;
}

/* suppress -Wvirtual-overloaded warnings TODO better to always use pyobj *? */
template<class K, class V> __ss_bool dict<K,V>::__lt__(pyobj *) { return False; }
template<class K, class V> __ss_bool dict<K,V>::__gt__(pyobj *) { return False; }
template<class K, class V> __ss_bool dict<K,V>::__ge__(pyobj *) { return False; }
template<class K, class V> __ss_bool dict<K,V>::__le__(pyobj *) { return False; }

template<class K, class V> __ss_bool dict<K,V>::__ge__(dict<K,V> *s) {
    throw new NotImplementedError();
}

template<class K, class V> __ss_bool dict<K,V>::__le__(dict<K,V> *s) {
    throw new NotImplementedError();
}

template<class K, class V> __ss_bool dict<K,V>::__lt__(dict<K,V> *s) {
    throw new NotImplementedError();
}

template<class K, class V> __ss_bool dict<K,V>::__gt__(dict<K,V> *s) {
    throw new NotImplementedError();
}

template <class K, class V> void *dict<K,V>::__setitem__(K key, V value)
{
    gcd[key] = value;
    return NULL;
}

template<class T> T __none() { return NULL; }
template<> int __none();
template<> __ss_float __none();

template <class K, class V> V dict<K,V>::__getitem__(K key) {
    typename __GC_DICT<K, V>::iterator it = gcd.find(key);
    if (it == gcd.end())
        throw new KeyError(repr(key));
    else
        return (*it).second;
}

template<class K, class V> void *dict<K,V>::__addtoitem__(K key, V value) {
    typename __GC_DICT<K, V>::iterator it = gcd.find(key);
    if (it == gcd.end())
        throw new KeyError(repr(key));
    else
        (*it).second = __add((*it).second, value);

    return NULL;
}

template <class K, class V> V dict<K,V>::get(K key) {
    typename __GC_DICT<K, V>::iterator it = gcd.find(key);
    if (it == gcd.end())
        return __none<V>();
    else
        return (*it).second;
}

template <class K, class V> V dict<K,V>::get(K key, V d) {
    typename __GC_DICT<K, V>::iterator it = gcd.find(key);
    if (it == gcd.end())
        return d;
    else
        return (*it).second;
}

template <class K, class V> V dict<K,V>::setdefault(K key, V value)
{
    typename __GC_DICT<K, V>::iterator it = gcd.find(key);
    if (it == gcd.end()) {
        gcd[key] = value;
        return value;
    } else {
        return (*it).second;
    }
}

template <class K, class V> void *dict<K,V>::__delitem__(K key) {
    typename __GC_DICT<K, V>::iterator it = gcd.find(key);
    if (it == gcd.end())
        throw new KeyError(repr(key));
    else
        gcd.erase(it);

    return NULL;
}

template<class K, class V> V dict<K,V>::pop(K key) {
    typename __GC_DICT<K, V>::iterator it = gcd.find(key);
    if (it == gcd.end())
        throw new KeyError(repr(key));
    else {
        V v = (*it).second;
        gcd.erase(it);
        return v;
    }
}

template<class K, class V> V dict<K,V>::pop(K key, V value) {
    typename __GC_DICT<K, V>::iterator it = gcd.find(key);
    if (it == gcd.end())
        return value;
    else {
        V v = (*it).second;
        gcd.erase(it);
        return v;
    }
}

template<class K, class V> tuple2<K,V> *dict<K,V>::popitem() {
    typename __GC_DICT<K, V>::iterator it = gcd.begin();
    if(it == gcd.end())
        throw new KeyError(new str("popitem(): dictionary is empty"));
    else {
        tuple2<K,V> *t = new tuple2<K,V>(2, (*it).first, (*it).second);
        gcd.erase(it);
        return t;
    }
}

template<class K, class V> str *dict<K,V>::__repr__() {
    str *r = new str("{");
    int i = __len__();

    for (const auto& [key, value] : gcd) {
        *r += repr(key)->c_str();
        *r += ": ";
        *r += repr(value)->c_str();
        if(--i > 0)
            *r += ", ";
    }

    *r += "}";
    return r;

}

template<class K, class V> __ss_int dict<K,V>::__len__() {
    return (__ss_int)gcd.size();
}

template <class K, class V> __ss_bool dict<K,V>::__contains__(K key) {
    return __mbool(gcd.find(key) != gcd.end());
}


template <class K, class V> __ss_bool dict<K,V>::has_key(K key) {
	return __contains__(key);
}

template <class K, class V> void *dict<K,V>::clear()
{
    gcd.clear();
    return NULL;
}

template <class K, class V> void *dict<K,V>::update(dict<K,V>* other)
{
   for (const auto& [key, value] : other->gcd)
       gcd[key] = value;

    return NULL;
}

template <class K, class V> template<class U> void *dict<K,V>::update(U *iter) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
		__setitem__(e->__getitem__(0), e->__getitem__(1));
    END_FOR
    return NULL;
}

template<class K, class V> dict<K,V> *dict<K,V>::copy() {
    dict<K,V> *c = new dict<K,V>;
    c->gcd = gcd;
    return c;
}

template<class K, class V> dict<K,V> *dict<K,V>::__copy__() {
    dict<K,V> *c = new dict<K,V>;
    c->gcd = gcd;
    return c;
}

template<class K, class V> dict<K,V> *dict<K,V>::__deepcopy__(dict<void *, pyobj *> *memo) {
    dict<K,V> *c = new dict<K,V>();
    memo->__setitem__(this, c);
    K e;
    typename dict<K,V>::for_in_loop __3;
    int __2;
    dict<K,V> *__1;
    FOR_IN(e,this,1,2,3)
        c->__setitem__(__deepcopy(e, memo), __deepcopy(this->__getitem__(e), memo));
    END_FOR
    return c;
}

/* dictiterkeys/values/items */

template<class K, class V> __dictiterkeys<K, V>::__dictiterkeys(dict<K,V> *d) {
    this->it = d->gcd.begin();
}

template<class K, class V> K __dictiterkeys<K, V>::__next__() {
    if(it == p->gcd.end())
        __throw_stop_iteration();

    return (*it++).first;
}

template<class K, class V> __dictitervalues<K, V>::__dictitervalues(dict<K,V> *d) {
    this->it = d->gcd.begin();
}

template<class K, class V> V __dictitervalues<K, V>::__next__() {
    if(it == p->gcd.end())
        __throw_stop_iteration();

    return (*it++).second;
}

template<class K, class V> __dictiteritems<K, V>::__dictiteritems(dict<K,V> *d) {
    this->it = d->gcd.begin();
}

template<class K, class V> tuple2<K, V> *__dictiteritems<K, V>::__next__() {
    if(it == p->gcd.end())
        __throw_stop_iteration();

    tuple2<K, V> *t = new tuple2<K, V>(2, (*it).first, (*it).second);
    it++;
    return t;
}

/* dict.fromkeys */

namespace __dict__ {
    template<class A, class B> dict<A, B> *fromkeys(pyiter<A> *f, B b) {
        dict<A, B> *d = new dict<A, B>();
        typename pyiter<A>::for_in_unit e;
        typename pyiter<A>::for_in_loop __3;
        int __2;
        pyiter<A> *__1;
        FOR_IN(e,f,1,2,3)
            d->__setitem__(e, b);
        END_FOR
        return d;
    }

    template<class A> dict<A, void *> *fromkeys(pyiter<A> *f) {
        return fromkeys(f, (void *)0);
    }

}
