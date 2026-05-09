"""
Android Boilerplate Generator - Genera plantillas completas para Android

Templates predefinidos:
- Activity completa con layout XML
- Fragment con ViewModel
- RecyclerView Adapter
- Custom View básico
- Service básico
- BroadcastReceiver

Uso:
    from agent.actions.tools.android_boilerplate import generate_android_boilerplate
    
    codigo = generate_android_boilerplate("Activity", "LoginScreen")
    # Genera LoginScreen.java + activity_login_screen.xml
"""

import re
from typing import Dict, Optional


class AndroidBoilerplateGenerator:
    """Generador de código boilerplate para Android"""
    
    def __init__(self):
        self.templates = {
            'activity': self._generate_activity_template,
            'fragment': self._generate_fragment_template,
            'adapter': self._generate_adapter_template,
            'custom_view': self._generate_custom_view_template,
            'service': self._generate_service_template,
            'broadcast_receiver': self._generate_broadcast_receiver_template,
        }
    
    def generate(self, component_type: str, name: str, **kwargs) -> Dict[str, str]:
        """
        Generar código boilerplate para un componente Android
        
        Args:
            component_type: Tipo de componente (activity, fragment, adapter, etc.)
            name: Nombre del componente (ej: LoginScreen)
            **kwargs: Parámetros adicionales según el tipo
            
        Returns:
            Diccionario con archivos generados {nombre_archivo: contenido}
        """
        generator = self.templates.get(component_type.lower())
        
        if not generator:
            raise ValueError(f"Tipo de componente no soportado: {component_type}. "
                           f"Opciones válidas: {', '.join(self.templates.keys())}")
        
        return generator(name, **kwargs)
    
    def _generate_activity_template(self, name: str, **kwargs) -> Dict[str, str]:
        """Generar template de Activity completa"""
        
        # Convertir a formato snake_case para nombres de recursos
        layout_name = self._to_snake_case(name).replace('_screen', '').replace('_activity', '')
        layout_file = f"activity_{layout_name}.xml"
        
        java_code = f"""package com.example.app;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.view.View;
import android.util.Log;

public class {name} extends AppCompatActivity {{

    private static final String TAG = "{name}";
    
    // Views
    private EditText editTextEmail;
    private EditText editTextPassword;
    private Button buttonLogin;
    private TextView textViewError;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.{layout_file.replace('.xml', '')});
        
        initializeViews();
        setupListeners();
    }}
    
    private void initializeViews() {{
        editTextEmail = findViewById(R.id.editTextEmail);
        editTextPassword = findViewById(R.id.editTextPassword);
        buttonLogin = findViewById(R.id.buttonLogin);
        textViewError = findViewById(R.id.textViewError);
    }}
    
    private void setupListeners() {{
        buttonLogin.setOnClickListener(new View.OnClickListener() {{
            @Override
            public void onClick(View v) {{
                handleLogin();
            }}
        }});
    }}
    
    private void handleLogin() {{
        String email = editTextEmail.getText().toString().trim();
        String password = editTextPassword.getText().toString().trim();
        
        // Validación básica
        if (email.isEmpty() || password.isEmpty()) {{
            textViewError.setText("Por favor completa todos los campos");
            textViewError.setVisibility(View.VISIBLE);
            return;
        }}
        
        Log.d(TAG, "Intentando login con email: " + email);
        
        // TODO: Implementar lógica de autenticación
        performLogin(email, password);
    }}
    
    private void performLogin(String email, String password) {{
        // Aquí va la lógica de autenticación
        // Ejemplo: llamada a API, Firebase Auth, etc.
    }}
}}
"""
        
        xml_layout = f"""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="24dp"
    android:gravity="center">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="{name}"
        android:textSize="24sp"
        android:textStyle="bold"
        android:layout_marginBottom="32dp"/>

    <EditText
        android:id="@+id/editTextEmail"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Email"
        android:inputType="textEmailAddress"
        android:layout_marginBottom="16dp"
        android:padding="12dp"/>

    <EditText
        android:id="@+id/editTextPassword"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Contraseña"
        android:inputType="textPassword"
        android:layout_marginBottom="24dp"
        android:padding="12dp"/>

    <Button
        android:id="@+id/buttonLogin"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Iniciar Sesión"
        android:padding="12dp"/>

    <TextView
        android:id="@+id/textViewError"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:textColor="#FF0000"
        android:visibility="gone"
        android:layout_marginTop="16dp"
        android:gravity="center"/>

</LinearLayout>
"""
        
        manifest_entry = f"""<!-- Agregar en AndroidManifest.xml -->
<activity android:name=".{name}"
    android:exported="false" />
"""
        
        return {
            f"{name}.java": java_code,
            f"res/layout/{layout_file}": xml_layout,
            "AndroidManifest.xml (snippet)": manifest_entry
        }
    
    def _generate_fragment_template(self, name: str, **kwargs) -> Dict[str, str]:
        """Generar template de Fragment con ViewModel"""
        
        layout_name = self._to_snake_case(name).replace('_fragment', '')
        layout_file = f"fragment_{layout_name}.xml"
        
        java_code = f"""package com.example.app;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;

public class {name} extends Fragment {{

    private {name}ViewModel viewModel;
    private TextView textViewData;
    private Button buttonAction;

    public static {name} newInstance() {{
        return new {name}();
    }}

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        viewModel = new ViewModelProvider(this).get({name}ViewModel.class);
    }}

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, 
                             @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {{
        return inflater.inflate(R.layout.{layout_file.replace('.xml', '')}, container, false);
    }}

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {{
        super.onViewCreated(view, savedInstanceState);
        
        initializeViews(view);
        setupObservers();
        setupListeners();
    }}
    
    private void initializeViews(View view) {{
        textViewData = view.findViewById(R.id.textViewData);
        buttonAction = view.findViewById(R.id.buttonAction);
    }}
    
    private void setupObservers() {{
        viewModel.getData().observe(getViewLifecycleOwner(), data -> {{
            textViewData.setText(data);
        }});
    }}
    
    private void setupListeners() {{
        buttonAction.setOnClickListener(v -> {{
            viewModel.performAction();
        }});
    }}
}}
"""
        
        viewmodel_code = f"""package com.example.app;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;

public class {name}ViewModel extends ViewModel {{

    private final MutableLiveData<String> data = new MutableLiveData<>();

    public LiveData<String> getData() {{
        return data;
    }}

    public void performAction() {{
        // TODO: Implementar lógica
        data.setValue("Acción realizada");
    }}
}}
"""
        
        xml_layout = f"""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    android:gravity="center">

    <TextView
        android:id="@+id/textViewData"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Datos del Fragment"
        android:textSize="18sp"
        android:layout_marginBottom="24dp"/>

    <Button
        android:id="@+id/buttonAction"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Realizar Acción"/>

</LinearLayout>
"""
        
        return {
            f"{name}.java": java_code,
            f"{name}ViewModel.java": viewmodel_code,
            f"res/layout/{layout_file}": xml_layout
        }
    
    def _generate_adapter_template(self, name: str, **kwargs) -> Dict[str, str]:
        """Generar template de RecyclerView Adapter"""
        
        item_type = kwargs.get('item_type', 'Item')
        layout_name = self._to_snake_case(name).replace('_adapter', '')
        item_layout_file = f"item_{layout_name}.xml"
        
        java_code = f"""package com.example.app;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class {name} extends RecyclerView.Adapter<{name}.{name}ViewHolder> {{

    private List<{item_type}> itemList;
    private OnItemClickListener listener;

    public interface OnItemClickListener {{
        void onItemClick({item_type} item, int position);
    }}

    public {name}(List<{item_type}> itemList, OnItemClickListener listener) {{
        this.itemList = itemList;
        this.listener = listener;
    }}

    @NonNull
    @Override
    public {name}ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {{
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.{item_layout_file.replace('.xml', '')}, parent, false);
        return new {name}ViewHolder(view);
    }}

    @Override
    public void onBindViewHolder(@NonNull {name}ViewHolder holder, int position) {{
        {item_type} item = itemList.get(position);
        holder.bind(item, listener);
    }}

    @Override
    public int getItemCount() {{
        return itemList.size();
    }}

    public void updateList(List<{item_type}> newList) {{
        itemList = newList;
        notifyDataSetChanged();
    }}

    static class {name}ViewHolder extends RecyclerView.ViewHolder {{
        private TextView textViewTitle;
        private TextView textViewDescription;

        public {name}ViewHolder(@NonNull View itemView) {{
            super(itemView);
            textViewTitle = itemView.findViewById(R.id.textViewTitle);
            textViewDescription = itemView.findViewById(R.id.textViewDescription);
        }}

        public void bind({item_type} item, OnItemClickListener listener) {{
            textViewTitle.setText(item.getTitle());
            textViewDescription.setText(item.getDescription());
            
            itemView.setOnClickListener(v -> {{
                if (listener != null) {{
                    listener.onItemClick(item, getAdapterPosition());
                }}
            }});
        }}
    }}
}}
"""
        
        item_layout = f"""<?xml version="1.0" encoding="utf-8"?>
<androidx.cardview.widget.CardView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_margin="8dp"
    app:cardCornerRadius="8dp"
    app:cardElevation="4dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">

        <TextView
            android:id="@+id/textViewTitle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="18sp"
            android:textStyle="bold"
            android:layout_marginBottom="8dp"/>

        <TextView
            android:id="@+id/textViewDescription"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="14sp"
            android:textColor="#666666"/>

    </LinearLayout>

</androidx.cardview.widget.CardView>
"""
        
        model_class = f"""package com.example.app;

public class {item_type} {{
    private String title;
    private String description;

    public {item_type}(String title, String description) {{
        this.title = title;
        this.description = description;
    }}

    public String getTitle() {{ return title; }}
    public String getDescription() {{ return description; }}
}}
"""
        
        return {
            f"{name}.java": java_code,
            f"{item_type}.java": model_class,
            f"res/layout/{item_layout_file}": item_layout
        }
    
    def _generate_custom_view_template(self, name: str, **kwargs) -> Dict[str, str]:
        """Generar template de Custom View"""
        
        java_code = f"""package com.example.app;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;
import androidx.annotation.Nullable;

public class {name} extends View {{

    private Paint paint;
    private float radius = 100f;

    public {name}(Context context) {{
        this(context, null);
    }}

    public {name}(Context context, @Nullable AttributeSet attrs) {{
        this(context, attrs, 0);
    }}

    public {name}(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {{
        super(context, attrs, defStyleAttr);
        init();
    }}

    private void init() {{
        paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        paint.setColor(0xFF2196F3); // Azul Material Design
        paint.setStyle(Paint.Style.FILL);
    }}

    @Override
    protected void onDraw(Canvas canvas) {{
        super.onDraw(canvas);
        
        int centerX = getWidth() / 2;
        int centerY = getHeight() / 2;
        
        canvas.drawCircle(centerX, centerY, radius, paint);
    }}

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {{
        int size = Math.min(
            MeasureSpec.getSize(widthMeasureSpec),
            MeasureSpec.getSize(heightMeasureSpec)
        );
        setMeasuredDimension(size, size);
    }}

    public void setRadius(float radius) {{
        this.radius = radius;
        invalidate();
    }}

    public void setColor(int color) {{
        paint.setColor(color);
        invalidate();
    }}
}}
"""
        
        usage_xml = f"""<!-- Uso en layout XML -->
<com.example.app.{name}
    android:layout_width="200dp"
    android:layout_height="200dp"
    android:layout_gravity="center"/>
"""
        
        return {
            f"{name}.java": java_code,
            "Uso en XML": usage_xml
        }
    
    def _generate_service_template(self, name: str, **kwargs) -> Dict[str, str]:
        """Generar template de Service"""
        
        java_code = f"""package com.example.app;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;
import androidx.annotation.Nullable;

public class {name} extends Service {{

    private static final String TAG = "{name}";

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {{
        return null;
    }}

    @Override
    public void onCreate() {{
        super.onCreate();
        Log.d(TAG, "Service creado");
    }}

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {{
        Log.d(TAG, "Service iniciado");
        
        // TODO: Implementar lógica del servicio
        // Ejemplo: descargar datos, reproducir música, etc.
        
        return START_STICKY;
    }}

    @Override
    public void onDestroy() {{
        super.onDestroy();
        Log.d(TAG, "Service destruido");
    }}
}}
"""
        
        manifest_entry = f"""<!-- Agregar en AndroidManifest.xml -->
<service android:name=".{name}"
    android:exported="false" />
"""
        
        return {
            f"{name}.java": java_code,
            "AndroidManifest.xml (snippet)": manifest_entry
        }
    
    def _generate_broadcast_receiver_template(self, name: str, **kwargs) -> Dict[str, str]:
        """Generar template de BroadcastReceiver"""
        
        java_code = f"""package com.example.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

public class {name} extends BroadcastReceiver {{

    private static final String TAG = "{name}";

    @Override
    public void onReceive(Context context, Intent intent) {{
        String action = intent.getAction();
        Log.d(TAG, "Broadcast recibido: " + action);
        
        // TODO: Manejar el broadcast
        if (action != null) {{
            switch (action) {{
                case Intent.ACTION_BATTERY_LOW:
                    handleBatteryLow(context);
                    break;
                case Intent.ACTION_POWER_CONNECTED:
                    handlePowerConnected(context);
                    break;
                default:
                    Log.w(TAG, "Acción no manejada: " + action);
            }}
        }}
    }}
    
    private void handleBatteryLow(Context context) {{
        Log.d(TAG, "Batería baja detectada");
        // Implementar lógica
    }}
    
    private void handlePowerConnected(Context context) {{
        Log.d(TAG, "Cargador conectado");
        // Implementar lógica
    }}
}}
"""
        
        manifest_entry = f"""<!-- Registrar en AndroidManifest.xml o dinámicamente en código -->
<receiver android:name=".{name}"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BATTERY_LOW" />
        <action android:name="android.intent.action.ACTION_POWER_CONNECTED" />
    </intent-filter>
</receiver>
"""
        
        return {
            f"{name}.java": java_code,
            "Registro (snippet)": manifest_entry
        }
    
    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convertir CamelCase a snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# Función de conveniencia para uso directo
def generate_android_boilerplate(component_type: str, name: str, **kwargs) -> Dict[str, str]:
    """
    Generar código boilerplate Android
    
    Args:
        component_type: 'activity', 'fragment', 'adapter', 'custom_view', 'service', 'broadcast_receiver'
        name: Nombre del componente
        **kwargs: Parámetros adicionales
        
    Returns:
        Diccionario {nombre_archivo: contenido}
    """
    generator = AndroidBoilerplateGenerator()
    return generator.generate(component_type, name, **kwargs)
