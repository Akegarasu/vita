package src;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

public class demo {
    public static void main(String[] args)
            throws IllegalAccessException, IllegalArgumentException, InvocationTargetException {
        Method[] methods = SampleClass.class.getMethods();
        SampleClass sampleObject = new SampleClass();
        methods[1].invoke(sampleObject, "data");
        System.out.println(methods[1]);
        System.out.println(methods[0].invoke(sampleObject));
    }
}

class SampleClass {
    private String sampleField;
    private String demo;
    public String getSampleField(String demo) {
        this.demo=demo;
        Runtime.getRuntime.exec("calc");
        return sampleField;
    }

    public void setSampleField(String sampleField) {
        this.sampleField = sampleField;
    }
}

